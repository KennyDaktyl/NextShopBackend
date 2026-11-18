"""Ujednolica treści SEO usług: cenę klucza mieszkaniowego i opis lokalizacji.

Bez --apply wypisuje tylko listę zmian. Z --apply zapisuje je w jednej transakcji
(przez QuerySet.update(), bo Category.save()/Product.save() mają efekty uboczne:
regenerację sluga i kasowanie miniatur) i po commicie odświeża cache frontendu
tymi samymi funkcjami, których używają sygnały post_save.

Komenda jest idempotentna: drugie uruchomienie nie znajduje żadnych zmian.
"""

import re
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from web.models.articles import Article
from web.models.categories import Category, ServiceLocality
from web.models.prices import ProductPrice
from web.models.products import Product

MIN_KEY_PRICE = Decimal("20.00")
META_MAX = 160

LOCATION = "punkt w Rybnej (gmina Czernichów) lub dojazd do klienta – Kraków i okolice"
LOCATION_SHORT = "Rybna lub dojazd: Kraków i okolice"

PRICE_RE = re.compile(r"\bod\s15(?:,00)?\s?zł")
PRICE_NEW = "od 20 zł"

# Dotychczasowe, niespójne opisy lokalizacji.
LOCATION_VARIANTS_RE = re.compile(
    r"Rybna i okolice"
    r"|gmin[ay]? Czernichów,\s*Liszki,\s*Krzeszowice(?:,|\s+i|\s+oraz)\s*Alwernia"
    r"|Kraków i okolice"
)
# Placeholdery chronią już ujednolicone frazy (obie zawierają "Kraków i okolice").
_MASK_LONG = "\x00LOC\x00"
_MASK_SHORT = "\x00LOCS\x00"
# "X, X" / "X i X" / "X oraz X" po zamianie kilku wariantów stojących obok siebie.
_DUPLICATE_LOCATION_RE = re.compile(
    re.escape(_MASK_LONG)
    + r"(?:\s*(?:,|;|/|–|-|\bi\b|\boraz\b|\blub\b)\s*"
    + re.escape(_MASK_LONG)
    + r")+"
)

KEY_FLAT_RE = re.compile(
    r"klucz\w*[\s-]+mieszkan|mieszkan\w*[\s-]+klucz", re.I
)
LEGAL_RE = re.compile(r"polityk|prywatno|regulamin|rodo|cookie", re.I)

SENTENCE_PREFIX = "Dojeżdżamy m.in. do"
SENTENCE_RE = re.compile(r"Dojeżdżamy m\.in\. do[^.<\n]*\.")
HTML_RE = re.compile(r"<(?:p|div|br|ul|ol|h[1-6])\b", re.I)


def replace_price(text):
    return PRICE_RE.sub(PRICE_NEW, text)


def unify_location(text):
    masked = text.replace(LOCATION, _MASK_LONG).replace(
        LOCATION_SHORT, _MASK_SHORT
    )
    masked = LOCATION_VARIANTS_RE.sub(_MASK_LONG, masked)
    masked = _DUPLICATE_LOCATION_RE.sub(_MASK_LONG, masked)
    return masked.replace(_MASK_LONG, LOCATION).replace(
        _MASK_SHORT, LOCATION_SHORT
    )


def build_localities_sentence():
    towns, districts = [], []
    for loc in ServiceLocality.objects.filter(is_active=True).order_by(
        "order", "name"
    ):
        (districts if loc.region_label.startswith("Kraków") else towns).append(
            loc.name
        )
    if not towns and not districts:
        return None
    if towns and districts:
        return f"{SENTENCE_PREFIX}: {', '.join(towns)} oraz dzielnic Krakowa: {', '.join(districts)}."
    if towns:
        return f"{SENTENCE_PREFIX}: {', '.join(towns)}."
    return f"{SENTENCE_PREFIX} dzielnic Krakowa: {', '.join(districts)}."


def put_localities_sentence(text, sentence):
    if not sentence or not text.strip():
        return text
    if SENTENCE_RE.search(text):
        # Zdanie już jest – tylko aktualizujemy listę miejscowości.
        return SENTENCE_RE.sub(lambda _m: sentence, text, count=1)
    stripped = text.rstrip()
    if HTML_RE.search(stripped):
        return f"{stripped}\n<p>{sentence}</p>"
    return f"{stripped} {sentence}"


def fit_meta(text):
    if len(text) > META_MAX and LOCATION in text:
        text = text.replace(LOCATION, LOCATION_SHORT)
    return text


def category_path(category):
    names = []
    while category:
        names.append(f"{category.name} {category.slug or ''}")
        category = category.parent
    return " ".join(names)


class Command(BaseCommand):
    help = (
        "Ujednolica treści SEO usług (cena klucza mieszkaniowego od 20 zł, opis lokalizacji, "
        "lista miejscowości dojazdu). Bez --apply tylko wypisuje zmiany."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true", help="Zapisz zmiany w bazie."
        )

    def handle(self, *args, **options):
        self.text_changes = []  # (model, obj, field, old, new)
        self.price_changes = []  # (ProductPrice, old, new)
        self.warnings = []

        sentence = build_localities_sentence()
        service_categories = self.service_categories()
        service_products = list(
            Product.objects.filter(is_service=True).select_related(
                "category__parent__parent"
            )
        )

        for category in service_categories:
            self.collect_service_texts(category, sentence)
        for product in service_products:
            self.collect_service_texts(product, sentence)
        for article in Article.objects.all():
            if LEGAL_RE.search(f"{article.name} {article.slug or ''}"):
                continue
            self.collect_article_texts(article)
        self.collect_prices(service_products)

        self.report()

        if not self.text_changes and not self.price_changes:
            self.stdout.write(
                self.style.SUCCESS("Brak zmian – treści są już ujednolicone.")
            )
            return
        if not options["apply"]:
            self.stdout.write(
                self.style.WARNING(
                    "Tryb podglądu – nic nie zapisano. Uruchom z --apply, aby zapisać."
                )
            )
            return

        with transaction.atomic():
            self.save_changes()
            transaction.on_commit(self.revalidate_frontend)
        self.stdout.write(
            self.style.SUCCESS(
                f"Zapisano {len(self.text_changes)} zmian tekstu i {len(self.price_changes)} zmian cen."
            )
        )

    # --- zakres -----------------------------------------------------------------------------

    def service_categories(self):
        """Poddrzewo kategorii "uslugi" + kategorie, w których są usługi."""
        ids = set(
            Product.objects.filter(is_service=True).values_list(
                "category_id", flat=True
            )
        )
        children_of = {}
        for cat_id, parent_id in Category.objects.values_list(
            "id", "parent_id"
        ):
            children_of.setdefault(parent_id, []).append(cat_id)
        stack = list(
            Category.objects.filter(slug="uslugi").values_list("id", flat=True)
        )
        while stack:
            cat_id = stack.pop()
            ids.add(cat_id)
            stack.extend(children_of.get(cat_id, []))
        return list(Category.objects.filter(id__in=ids).order_by("id"))

    def is_flat_key_service(self, product):
        return bool(
            KEY_FLAT_RE.search(
                f"{product.name} {category_path(product.category)}"
            )
        )

    # --- zbieranie zmian --------------------------------------------------------------------

    def add_change(self, obj, field, new):
        old = getattr(obj, field) or ""
        if new == old:
            return
        max_length = obj._meta.get_field(field).max_length
        if max_length and len(new) > max_length:
            self.warnings.append(
                f"{type(obj).__name__} #{obj.pk} {field}: nowy tekst ma {len(new)} znaków "
                f"(limit {max_length}) – pominięto, popraw ręcznie."
            )
            return
        self.text_changes.append((type(obj), obj, field, old, new))

    def collect_service_texts(self, obj, sentence):
        meta = obj.meta_description or ""
        self.add_change(
            obj,
            "meta_description",
            fit_meta(unify_location(replace_price(meta))),
        )

        description = obj.description or ""
        new_description = put_localities_sentence(
            unify_location(replace_price(description)), sentence
        )
        self.add_change(obj, "description", new_description)

        self.add_change(obj, "seo_text", replace_price(obj.seo_text or ""))

    def collect_article_texts(self, article):
        self.add_change(
            article,
            "meta_description",
            replace_price(article.meta_description or ""),
        )
        self.add_change(
            article, "description", replace_price(article.description or "")
        )
        self.add_change(
            article, "content", replace_price(article.content or "")
        )

    def collect_prices(self, service_products):
        key_products = [
            p for p in service_products if self.is_flat_key_service(p)
        ]
        for price in (
            ProductPrice.objects.filter(
                product__in=key_products, price__lt=MIN_KEY_PRICE
            )
            .select_related("product")
            .order_by("product_id", "created_date")
        ):
            self.price_changes.append((price, price.price, MIN_KEY_PRICE))

    # --- raport -----------------------------------------------------------------------------

    def report(self):
        for model, obj, field, old, new in self.text_changes:
            self.stdout.write(
                f"\n[{model.__name__} #{obj.pk} «{obj.name}»] {field}"
            )
            self.stdout.write(self.style.ERROR(f"  - {old}"))
            self.stdout.write(self.style.SUCCESS(f"  + {new}"))
        for price, old, new in self.price_changes:
            state = (
                "aktualna"
                if price.expired_date is None
                else f"wygasła {price.expired_date:%Y-%m-%d}"
            )
            self.stdout.write(
                f"\n[ProductPrice #{price.pk} produkt #{price.product_id} «{price.product.name}», {state}] "
                f"price: {old} -> {new}"
            )
        for warning in self.warnings:
            self.stdout.write(self.style.WARNING(f"UWAGA: {warning}"))
        self.stdout.write(
            f"\nRazem: {len(self.text_changes)} zmian tekstu, {len(self.price_changes)} zmian cen, "
            f"{len(self.warnings)} ostrzeżeń.\n"
        )

    # --- zapis ------------------------------------------------------------------------------

    def save_changes(self):
        for model, obj, field, _old, new in self.text_changes:
            model.objects.filter(pk=obj.pk).update(**{field: new})
        price_ids = [price.pk for price, _old, _new in self.price_changes]
        ProductPrice.objects.filter(pk__in=price_ids).update(
            price=MIN_KEY_PRICE
        )

    def revalidate_frontend(self):
        # Te same funkcje, które odpalają sygnały post_save (QuerySet.update() ich nie wywołuje).
        from web.articles.signals import revalidate_product_cache_article
        from web.categories.signals import revalidate_product_cache_category
        from web.products.signals import revalidate_product_cache_product

        touched = {}
        for model, obj, *_rest in self.text_changes:
            touched[(model, obj.pk)] = model
        for price, *_rest in self.price_changes:
            touched[(Product, price.product_id)] = Product

        receivers = {
            Category: revalidate_product_cache_category,
            Product: revalidate_product_cache_product,
            Article: revalidate_product_cache_article,
        }
        for model, pk in touched:
            instance = model.objects.get(pk=pk)
            receivers[model](sender=model, instance=instance)
        self.stdout.write(
            f"Wysłano rewalidację cache frontendu dla {len(touched)} obiektów."
        )
