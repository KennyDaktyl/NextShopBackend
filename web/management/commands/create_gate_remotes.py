"""Tworzy kategorię „Piloty do bram”, producentów i 13 pilotów do bram.

Bez --apply działa w transakcji wycofywanej na końcu (podgląd: nic nie zapisuje,
nie kopiuje plików i nie wysyła rewalidacji). Z --apply zapisuje wszystko w jednej
transakcji i po commicie odświeża cache frontendu.

Idempotentna: produkty są dopasowywane po SKU, a potem po slugu; drugie
uruchomienie nie tworzy duplikatów, tylko synchronizuje treści z
_gate_remotes_data.py. Cena (69 zł – tymczasowa) i stan magazynowy (1 szt.)
są ustawiane WYŁĄCZNIE przy tworzeniu produktu – później zmieniasz je w panelu,
a ponowne uruchomienie komendy podstawi nową cenę do meta title/description,
krótkiego opisu, FAQ i tytułu zdjęcia.

Zdjęcie: plik oryginału z pozycji usługowej jest kopiowany jako NOWY plik
(products/{slug}.{ext}), więc zmiana lub usunięcie zdjęcia usługi nie wpływa
na produkt. Miniatury generuje Product.save(). Gdy slug się zmieni, plik
i miniatury są zapisywane ponownie pod nową nazwą (stare pliki usuwają sygnały).

Uwaga: Product.save() nadpisuje slug na „{nazwa}-id-{id}” przy tworzeniu
i przy zmianie nazwy, dlatego nazwy i sluga zmieniamy przez QuerySet.update().
"""

import copy
import os
import re
from decimal import Decimal
from unittest import mock

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from web.management.commands import _gate_remotes_data as data
from web.models.categories import Category
from web.models.images import Photo, Thumbnail
from web.models.prices import ProductPrice
from web.models.products import (
    Brand,
    Product,
    ProductFAQ,
    ProductSpecification,
)

TITLE_MAX = 60
META_MAX = 160
META_RANGE = (140, 155)


class _DryRun(Exception):
    pass


def format_price(value):
    value = Decimal(value).quantize(Decimal("0.01"))
    if value == value.to_integral():
        return str(int(value))
    return f"{value:.2f}".replace(".", ",")


def meta_title(remote, price):
    for suffix in ("Serwis w Rybnej", "Rybna"):
        title = f"Pilot {remote['meta_label']} – {price} zł | {suffix}"
        if len(title) <= TITLE_MAX:
            return title
    raise CommandError(f"Meta title za długi: {title} ({len(title)})")


def product_texts(remote, brand_name, price):
    label = remote["label"]
    short = remote["short"].format(price=price)
    return {
        "name": remote["name"],
        "h1_tag": remote["name"],
        "short_description": short,
        "description": short,
        "seo_text": data.build_seo_text(remote, brand_name),
        "meta_title": meta_title(remote, price),
        "meta_description": remote["meta_description"].format(price=price),
        "image_alt": f"Pilot do bramy {label}, {remote['color']}",
        "image_title": f"{label} – pilot do bramy, {price} zł",
        "google_product_category": data.GOOGLE_PRODUCT_CATEGORY,
    }


class Command(BaseCommand):
    help = "Tworzy/synchronizuje kategorię „Piloty do bram” i 13 pilotów do bram."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true", help="Zapisz zmiany w bazie."
        )

    def handle(self, *args, **options):
        self.apply = options["apply"]
        self.changes = []
        self.warnings = []
        self.touched_products = set()
        self.old_slugs = {}  # pk -> poprzedni slug (do rewalidacji starego adresu)
        self.report_rows = []

        try:
            if self.apply:
                with transaction.atomic():
                    self.run()
                    transaction.on_commit(self.revalidate_frontend)
            else:
                # Sygnały post_save wysyłają rewalidację do Next.js – w podglądzie wyciszone.
                with mock.patch("requests.post"), transaction.atomic():
                    self.run()
                    raise _DryRun
        except _DryRun:
            pass

        self.print_report()
        if self.apply:
            self.stdout.write(
                self.style.SUCCESS(f"Zapisano. Liczba zmian: {len(self.changes)}.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Tryb podglądu – nic nie zapisano ({len(self.changes)} zmian). "
                    "Uruchom z --apply, aby zapisać."
                )
            )

    # --- kroki ------------------------------------------------------------------------------

    def run(self):
        self.brands = {slug: self.sync_brand(slug, d) for slug, d in data.BRANDS.items()}
        self.category = self.get_or_create_category()
        for remote in data.REMOTES:
            self.sync_product(remote)
        self.sync_category_texts()

    def change(self, what):
        self.changes.append(what)
        self.stdout.write(f"  • {what}")

    def sync_brand(self, slug, d):
        brand = Brand.objects.filter(slug=slug).first()
        if brand is None:
            for alias in d["aliases"]:
                brand = (
                    Brand.objects.filter(name__iexact=alias).order_by("id").first()
                )
                if brand:
                    break
        if brand is None:
            brand = Brand(name=d["name"])
            brand.save()
            self.change(f"Marka: utworzono {d['name']}")
        wanted = {
            "name": d["name"],
            "slug": slug,
            "description": d["description"],
            "website": d["website"],
        }
        diff = {k: v for k, v in wanted.items() if getattr(brand, k) != v}
        if diff:
            Brand.objects.filter(pk=brand.pk).update(**diff)
            brand.refresh_from_db()
            self.change(f"Marka {brand.pk}: {', '.join(diff)}")
        return brand

    def get_or_create_category(self):
        c = data.CATEGORY
        category = Category.objects.filter(slug=c["slug"]).first()
        if category is None:
            parent = Category.objects.filter(slug=c["parent_slug"]).first()
            if parent is None:
                raise CommandError(f"Brak kategorii nadrzędnej „{c['parent_slug']}”.")
            category = Category(name=c["name"], parent=parent, order=c["order"])
            category.save()
            if category.slug != c["slug"]:
                Category.objects.filter(pk=category.pk).update(slug=c["slug"])
                category.refresh_from_db()
            self.change(f"Kategoria: utworzono {category.get_full_path()}")
        return category

    def sync_category_texts(self):
        c = data.CATEGORY
        prices = [
            p.current_price
            for p in self.category.products.filter(is_active=True)
            if p.current_price is not None
        ]
        price = format_price(min(prices) if prices else data.DEFAULT_PRICE)
        wanted = {
            "item_label": c["item_label"],
            "h1_tag": c["h1_tag"],
            "meta_title": c["meta_title"].format(price=price),
            "meta_description": c["meta_description"].format(price=price),
            "description": c["description"].format(price=price),
            "seo_text": c["seo_text"],
            "is_active": True,
        }
        self.check_lengths(c["slug"], wanted["meta_title"], wanted["meta_description"])
        diff = {k: v for k, v in wanted.items() if getattr(self.category, k) != v}
        if diff:
            # update(), bo Category.save() regeneruje slug przy zmianie nazwy.
            Category.objects.filter(pk=self.category.pk).update(**diff)
            self.category.refresh_from_db()
            self.change(f"Kategoria {self.category.slug}: {', '.join(diff)}")
        self.category_row = {
            "url": f"/produkty/{self.category.slug}",
            "meta_title": wanted["meta_title"],
            "meta_description": wanted["meta_description"],
        }

    def check_lengths(self, key, title, description):
        if len(title) > TITLE_MAX:
            raise CommandError(f"{key}: meta title > {TITLE_MAX} znaków")
        if len(description) > META_MAX:
            raise CommandError(f"{key}: meta description > {META_MAX} znaków")
        lo, hi = META_RANGE
        if not lo <= len(description) <= hi and key != data.CATEGORY["slug"]:
            self.warnings.append(
                f"{key}: meta description ma {len(description)} znaków (cel {lo}–{hi})"
            )

    def sync_product(self, remote):
        product = (
            Product.objects.filter(sku=remote["sku"]).first()
            or Product.objects.filter(slug=remote["slug"]).first()
        )
        if product is not None and product.is_service:
            raise CommandError(
                f"Slug/SKU {remote['slug']} należy do usługi id={product.pk} – przerywam."
            )
        if product is None:
            product = Product(
                name=remote["name"],
                category=self.category,
                is_service=False,
                qty=data.DEFAULT_QTY,
            )
            product.save()
            ProductPrice(product=product, price=Decimal(data.DEFAULT_PRICE)).save()
            self.change(f"Produkt: utworzono {remote['slug']} (id {product.pk})")

        if product.slug != remote["slug"]:
            if product.slug and not re.search(r"-id-\d+$", product.slug):
                self.old_slugs[product.pk] = product.slug
            Product.objects.filter(pk=product.pk).update(slug=remote["slug"])
            self.change(f"{remote['slug']}: slug")
        product.refresh_from_db()

        compatible = self.brands[remote["compatible"]]
        price = format_price(product.current_price or data.DEFAULT_PRICE)
        texts = product_texts(remote, compatible.name, price)
        wanted = {
            **texts,
            "sku": remote["sku"],
            "category_id": self.category.pk,
            # Marka = producent dopiero po potwierdzeniu oryginalności, inaczej pusta.
            "brand_id": compatible.pk if remote.get("brand_is_manufacturer") else None,
            "compatible_brand_id": compatible.pk,
            "is_service": False,
        }
        self.check_lengths(remote["slug"], texts["meta_title"], texts["meta_description"])
        diff = {k: v for k, v in wanted.items() if getattr(product, k) != v}
        if diff:
            Product.objects.filter(pk=product.pk).update(**diff)
            product.refresh_from_db()
            self.change(f"{remote['slug']}: {', '.join(diff)}")
            self.touched_products.add(product.pk)

        self.sync_image(product, remote)
        self.sync_photos(product, remote)
        self.sync_related(
            product,
            ProductSpecification,
            [{"name": n, "value": v} for n, v in remote["specs"]],
            "specyfikacja",
        )
        self.sync_related(
            product,
            ProductFAQ,
            [{"question": q, "answer": a} for q, a in data.build_faqs(remote, price)],
            "FAQ",
        )

        self.report_rows.append(
            {
                "name": product.name,
                "slug": remote["slug"],
                "url": f"/produkt/{remote['slug']}",
                "sku": remote["sku"],
                "meta_title": texts["meta_title"],
                "meta_description": texts["meta_description"],
                "alt": texts["image_alt"],
                "title": texts["image_title"],
                "sources": data.SOURCES.get(remote["sources"]) if remote["sources"] else None,
            }
        )

    def sync_image(self, product, remote):
        if not product.oryg_image:
            source = Product.objects.filter(pk=remote["service_id"]).first()
            if source is None or not source.oryg_image:
                self.warnings.append(
                    f"{remote['slug']}: brak zdjęcia w usłudze id={remote['service_id']}"
                )
                return
            ext = os.path.splitext(source.oryg_image.name)[1].lower()
            self.change(
                f"{remote['slug']}: zdjęcie – kopia {source.oryg_image.name} → products/{remote['slug']}{ext}"
            )
            self.touched_products.add(product.pk)
            if not self.apply:
                return
            with source.oryg_image.open("rb") as f:
                content = f.read()
            # save() wygeneruje miniatury z nazwą wg sluga i z alt/title produktu.
            product.oryg_image.save(
                f"{remote['slug']}{ext}", ContentFile(content), save=False
            )
            product.save()
            return

        stem = os.path.splitext(os.path.basename(product.oryg_image.name))[0]
        # Django dokleja „_XXXXXXX”, gdy plik o tej nazwie już istnieje – to nadal aktualna nazwa.
        if not re.fullmatch(rf"{re.escape(remote['slug'])}(_[A-Za-z0-9]{{7}})?", stem):
            # Slug się zmienił – zapisujemy plik pod nową nazwą; save() usunie stary plik
            # i stare miniatury, a nowe wygeneruje z nazwą wg sluga.
            ext = os.path.splitext(product.oryg_image.name)[1].lower()
            self.change(
                f"{remote['slug']}: zdjęcie – nowa nazwa {product.oryg_image.name} → products/{remote['slug']}{ext}"
            )
            self.touched_products.add(product.pk)
            if not self.apply:
                return
            with product.oryg_image.open("rb") as f:
                content = f.read()
            product.oryg_image.save(
                f"{remote['slug']}{ext}", ContentFile(content), save=False
            )
            product.save()
            return

        # Zdjęcie już jest – synchronizujemy alt/title w miniaturach głównych.
        thumbs = Thumbnail.objects.filter(product=product, main=True, is_variant=False)
        stale = thumbs.exclude(alt=product.image_alt, title=product.image_title)
        if stale.exists():
            stale.update(alt=product.image_alt, title=product.image_title)
            self.change(f"{remote['slug']}: alt/title miniatur")
            self.touched_products.add(product.pk)

    def sync_photos(self, product, remote):
        if not remote.get("copy_photos"):
            return
        existing = list(product.photos.all())
        pattern = re.compile(rf"^{re.escape(remote['slug'])}-\d+(_[A-Za-z0-9]+)?\.\w+$")
        current = all(
            pattern.match(os.path.basename(p.oryg_image.name))
            and (p.image_alt or "").startswith(f"Pilot do bramy {remote['label']},")
            for p in existing
        )
        if existing and current:
            return
        if existing:
            # Nazwy plików/alt po starym slugu – usuwamy zdjęcia i ich miniatury
            # (miniatury dodatkowych zdjęć są przypięte do produktu, main=False).
            self.change(f"{remote['slug']}: dodatkowe zdjęcia – ponownie pod nową nazwą")
            self.touched_products.add(product.pk)
            if not self.apply:
                return
            sources = [(p.oryg_image.name, p.image_alt) for p in existing]
            contents = []
            for photo in existing:
                with photo.oryg_image.open("rb") as f:
                    contents.append(f.read())
            Thumbnail.objects.filter(product=product, main=False, is_variant=False).delete()
            for photo in existing:
                photo.delete()
            for index, ((name, alt), content) in enumerate(zip(sources, contents), start=1):
                suffix = alt.split(",")[-1].strip() if alt else f"zdjęcie {index}"
                self.create_photo(product, remote, index, suffix, os.path.splitext(name)[1].lower(), content)
            return
        source_photos = list(
            Photo.objects.filter(product_id=remote["service_id"]).order_by("id")
        )
        for index, source in enumerate(source_photos, start=1):
            suffix = (source.image_alt or "").split("025", 1)[-1].strip(" -–") or f"zdjęcie {index}"
            ext = os.path.splitext(source.oryg_image.name)[1].lower()
            self.change(f"{remote['slug']}: dodatkowe zdjęcie „{suffix}” (kopia {source.oryg_image.name})")
            self.touched_products.add(product.pk)
            if not self.apply:
                continue
            with source.oryg_image.open("rb") as f:
                self.create_photo(product, remote, index, suffix, ext, f.read())

    def create_photo(self, product, remote, index, suffix, ext, content):
        alt = f"Pilot do bramy {remote['label']}, {suffix}"
        photo = Photo(
            product=product,
            name=f"{remote['slug']}-{suffix}",
            image_alt=alt,
            image_title=alt,
        )
        photo.oryg_image.save(f"{remote['slug']}-{index}{ext}", ContentFile(content), save=False)
        photo.save()

    def sync_related(self, product, model, wanted, label):
        fields = list(wanted[0].keys()) if wanted else []
        current = list(
            model.objects.filter(product=product).order_by("order", "id").values(*fields)
        )
        if current == wanted:
            return
        model.objects.filter(product=product).delete()
        model.objects.bulk_create(
            [model(product=product, order=i, **row) for i, row in enumerate(wanted, start=1)]
        )
        self.change(f"{product.slug}: {label} ({len(wanted)})")
        self.touched_products.add(product.pk)

    # --- po zapisie -------------------------------------------------------------------------

    def revalidate_frontend(self):
        from web.categories.signals import revalidate_product_cache_category
        from web.products.signals import revalidate_product_cache_product

        for product in Product.objects.filter(pk__in=self.touched_products):
            revalidate_product_cache_product(sender=Product, instance=product)
            if product.pk in self.old_slugs:
                # Stary adres ma własny tag cache – bez tego serwowałby starą treść.
                old = copy.copy(product)
                old.slug = self.old_slugs[product.pk]
                revalidate_product_cache_product(sender=Product, instance=old)
        revalidate_product_cache_category(sender=Category, instance=self.category)
        self.stdout.write(
            f"Wysłano rewalidację cache frontendu ({len(self.touched_products)} produktów + kategoria)."
        )

    def print_report(self):
        for warning in self.warnings:
            self.stdout.write(self.style.WARNING(f"! {warning}"))
        if not self.report_rows:
            return
        out = self.stdout.write
        row = getattr(self, "category_row", None)
        if row:
            out("\n== Kategoria ==")
            out(f"{row['url']}\n  title ({len(row['meta_title'])}): {row['meta_title']}")
            out(f"  description ({len(row['meta_description'])}): {row['meta_description']}")
        out("\n== Produkty ==")
        for r in self.report_rows:
            out(f"{r['name']}\n  {r['url']}  SKU {r['sku']}")
            out(f"  title ({len(r['meta_title'])}): {r['meta_title']}")
            out(f"  description ({len(r['meta_description'])}): {r['meta_description']}")
            out(f"  alt: {r['alt']}\n  title zdjęcia: {r['title']}")
            if r["sources"]:
                out("  źródła faktów: " + "; ".join(r["sources"]))
            out(f"  FAQ (procedury): {data.GENERAL}")
