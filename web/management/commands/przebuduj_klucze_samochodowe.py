"""Przebudowa treści pod klucze samochodowe (2026-11-20).

Bez --apply: podgląd (transakcja wycofywana, rewalidacja wyciszona).
Z --apply: zapis w jednej transakcji + rewalidacja cache frontendu po commicie.
Idempotentna: drugie uruchomienie nie znajduje zmian.

Co robi (dane w _car_keys_data.py):
  * dokładne podmiany tekstów (ceny 180/150 zł, VAG po 2016, linki do nowych stron),
  * cena usługi kopiowania immobilizera → 300 zł (nowy rekord ProductPrice),
  * H1/title/opis kategorii mobilne-dorabianie-kluczy,
  * kolejność kategorii promowanych i banerów,
  * nowe kategorie: awaryjne otwieranie samochodów + Audi, Volkswagen, Seat (z FAQ).
Żaden istniejący slug nie jest zmieniany (zmiany przez QuerySet.update()).
"""

from decimal import Decimal
from unittest import mock

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from web.management.commands import _car_keys_data as data
from web.models.articles import Article
from web.models.categories import Category, CategoryFAQ
from web.models.heros import Hero
from web.models.prices import ProductPrice
from web.models.products import Product

MODELS = {"category": Category, "product": Product, "article": Article}


class _DryRun(Exception):
    pass


class Command(BaseCommand):
    help = "Przebudowa treści serwisu pod klucze samochodowe (podgląd; --apply zapisuje)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true", help="Zapisz zmiany w bazie."
        )

    def handle(self, *args, **options):
        self.apply = options["apply"]
        self.changes = []
        self.warnings = []
        self.touched = {
            "category": set(),
            "product": set(),
            "article": set(),
            "hero": set(),
        }
        try:
            if self.apply:
                with transaction.atomic():
                    self.run()
                    transaction.on_commit(self.revalidate_frontend)
            else:
                with mock.patch("requests.post"), transaction.atomic():
                    self.run()
                    raise _DryRun
        except _DryRun:
            pass

        for warning in self.warnings:
            self.stdout.write(self.style.WARNING(f"! {warning}"))
        if self.apply:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Zapisano. Liczba zmian: {len(self.changes)}."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Tryb podglądu – nic nie zapisano ({len(self.changes)} zmian). "
                    "Uruchom z --apply, aby zapisać."
                )
            )

    def change(self, kind, pk, what):
        self.changes.append(what)
        self.touched[kind].add(pk)
        self.stdout.write(f"  • {what}")

    # --- kroki ------------------------------------------------------------------------------

    def run(self):
        self.create_categories()
        self.apply_replacements()
        self.apply_category_fields()
        self.apply_prices()
        self.apply_orders()

    def get_category(self, slug):
        category = Category.objects.filter(slug=slug).first()
        if category is None:
            raise CommandError(f"Brak kategorii „{slug}”.")
        return category

    def ensure_category(self, spec, parent):
        category = Category.objects.filter(slug=spec["slug"]).first()
        if category is None:
            category = Category(
                name=spec["name"], parent=parent, order=spec.get("order", 1)
            )
            category.save()
            if category.slug != spec["slug"]:
                Category.objects.filter(pk=category.pk).update(
                    slug=spec["slug"]
                )
                category.refresh_from_db()
            self.change(
                "category",
                category.pk,
                f"Kategoria: utworzono {category.get_full_path()}",
            )
        wanted = {
            key: spec[key]
            for key in (
                "item_label",
                "meta_title",
                "meta_description",
                "h1_tag",
                "description",
                "seo_text",
            )
        }
        wanted.update({"parent_id": parent.pk, "is_active": True})
        self.update_fields(
            Category, category, wanted, "category", spec["slug"]
        )
        self.sync_faqs(category, spec["faqs"])
        return category

    def create_categories(self):
        emergency = data.NEW_EMERGENCY
        self.ensure_category(
            emergency, self.get_category(emergency["parent_slug"])
        )
        programming = self.get_category("programowanie-kluczy-samochodowych")
        for brand, spec in data.NEW_BRANDS.items():
            self.ensure_category(
                {
                    **spec,
                    "slug": f"programowanie-kluczy-i-pilotow-samochodowych-{brand}",
                },
                programming,
            )

    def update_fields(self, model, obj, wanted, kind, label):
        diff = {k: v for k, v in wanted.items() if getattr(obj, k) != v}
        if diff:
            # update(): Category.save() regeneruje slug przy zmianie nazwy, Product.save() też.
            model.objects.filter(pk=obj.pk).update(**diff)
            obj.refresh_from_db()
            self.change(kind, obj.pk, f"{label}: {', '.join(diff)}")

    def sync_faqs(self, category, faqs):
        wanted = [{"question": q, "answer": a} for q, a in faqs]
        current = list(
            category.faqs.order_by("order", "id").values("question", "answer")
        )
        if current == wanted:
            return
        category.faqs.all().delete()
        CategoryFAQ.objects.bulk_create(
            [
                CategoryFAQ(category=category, order=i, **row)
                for i, row in enumerate(wanted, start=1)
            ]
        )
        self.change(
            "category", category.pk, f"{category.slug}: FAQ ({len(wanted)})"
        )

    def apply_replacements(self):
        for kind, slug, field, old, new in data.REPLACEMENTS:
            model = MODELS[kind]
            qs = (
                model.objects.all()
                if slug is None
                else model.objects.filter(slug=slug)
            )
            if slug is not None and not qs.exists():
                self.warnings.append(f"{kind} {slug}: nie znaleziono obiektu")
                continue
            matched = 0
            for obj in qs:
                text = getattr(obj, field) or ""
                # Najpierw „już zrobione”: przy wstawkach nowy tekst zawiera stary fragment.
                if new in text:
                    matched += 1
                elif old in text:
                    model.objects.filter(pk=obj.pk).update(
                        **{field: text.replace(old, new, 1)}
                    )
                    self.change(
                        kind,
                        obj.pk,
                        f"{kind} {obj.slug}.{field}: podmiana „{old[:50]}…”",
                    )
                    matched += 1
            if slug is not None and not matched:
                self.warnings.append(
                    f"{kind} {slug}.{field}: nie znaleziono ani starego, ani nowego tekstu „{old[:50]}…” – sprawdź ręcznie"
                )

    def apply_category_fields(self):
        for slug, fields in data.CATEGORY_FIELDS.items():
            self.update_fields(
                Category, self.get_category(slug), fields, "category", slug
            )

    def apply_prices(self):
        for slug, price in data.PRODUCT_PRICES.items():
            product = Product.objects.filter(slug=slug).first()
            if product is None:
                self.warnings.append(f"Produkt {slug}: nie znaleziono")
                continue
            if product.current_price != Decimal(price):
                ProductPrice(product=product, price=Decimal(price)).save()
                self.change(
                    "product",
                    product.pk,
                    f"{slug}: cena {product.current_price} → {price}",
                )

    def apply_orders(self):
        for slug, order in data.CATEGORY_ORDER.items():
            category = Category.objects.filter(slug=slug).first()
            if category is None:
                self.warnings.append(f"Kolejność: brak kategorii „{slug}”")
                continue
            if category.order != order:
                Category.objects.filter(pk=category.pk).update(order=order)
                self.change(
                    "category",
                    category.pk,
                    f"{slug}: kolejność {category.order} → {order}",
                )
        for title, fields in data.HERO_FIELDS.items():
            hero = Hero.objects.filter(title=title).first()
            if hero is None:
                self.warnings.append(f"Baner „{title}”: nie znaleziono")
                continue
            diff = {k: v for k, v in fields.items() if getattr(hero, k) != v}
            if diff:
                # update(): Hero.save() regeneruje miniatury.
                Hero.objects.filter(pk=hero.pk).update(**diff)
                self.change(
                    "hero", hero.pk, f"Baner „{title}”: {', '.join(diff)}"
                )

    # --- po zapisie -------------------------------------------------------------------------

    def revalidate_frontend(self):
        from web.articles.signals import revalidate_product_cache_article
        from web.categories.signals import revalidate_product_cache_category
        from web.front.signals import revalidate_hero_cache
        from web.products.signals import revalidate_product_cache_product

        receivers = {
            "category": (Category, revalidate_product_cache_category),
            "product": (Product, revalidate_product_cache_product),
            "article": (Article, revalidate_product_cache_article),
            "hero": (Hero, revalidate_hero_cache),
        }
        count = 0
        for kind, pks in self.touched.items():
            model, receiver = receivers[kind]
            for obj in model.objects.filter(pk__in=pks):
                receiver(sender=model, instance=obj)
                count += 1
        self.stdout.write(
            f"Wysłano rewalidację cache frontendu ({count} obiektów)."
        )
