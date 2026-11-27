"""Naprawa tekstów alternatywnych zdjęć kategorii, produktów i artykułów.

python manage.py fix_image_alts --dry-run   # tylko lista zmian, nic nie zapisuje
python manage.py fix_image_alts             # zapis + rewalidacja cache frontendu

Gdy `image_alt` jest pusty, wygląda na slug/nazwę pliku albo jest placeholderem
(„Category Image”, „Thumbnail”, „Large Image”), dostaje nazwę obiektu. Potem alt/title
w istniejących miniaturach zdjęcia głównego są wyrównywane do pola (bez nowych plików).
Slugi, nazwy i ceny zostają nietknięte.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from web.models.articles import Article
from web.models.categories import Category
from web.models.images import is_technical_alt, sync_thumbnail_texts
from web.models.products import Product


class Command(BaseCommand):
    help = "Ustawia sensowne teksty alternatywne zdjęć i synchronizuje je z miniaturami."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Tylko wypisz zmiany, nic nie zapisuj.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        changes = []  # (label, obj, field_change|None, stale_thumbs)

        for model, label in ((Category, "Kategoria"), (Product, "Produkt"), (Article, "Artykuł")):
            for obj in model.objects.order_by("pk"):
                change = self.plan(obj)
                if change:
                    changes.append((label, obj, *change))

        self.print_report(changes)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Tryb --dry-run – nic nie zapisano ({len(changes)} obiektów do poprawy)."
                )
            )
            return
        if not changes:
            self.stdout.write(self.style.SUCCESS("Nic do poprawy."))
            return

        with transaction.atomic():
            for _label, obj, new_alt, _stale in changes:
                if new_alt is not None:
                    type(obj).objects.filter(pk=obj.pk).update(image_alt=new_alt)
                    obj.image_alt = new_alt
                sync_thumbnail_texts(obj.main_thumbnails, obj.image_alt_text, obj.image_title)
            transaction.on_commit(lambda: self.revalidate_frontend(changes))

        self.stdout.write(self.style.SUCCESS(f"Zapisano. Poprawiono {len(changes)} obiektów."))

    def plan(self, obj):
        """Zwraca (nowy image_alt albo None, lista starych altów miniatur) lub None."""
        if not obj.oryg_image:
            return None
        new_alt = None
        if is_technical_alt(obj.image_alt):
            new_alt = obj.name
        target_alt = new_alt or obj.image_alt.strip()
        target_title = (obj.image_title or "").strip()

        stale = []
        for thumb in obj.main_thumbnails:
            if thumb.alt != target_alt or (target_title and thumb.title != target_title):
                stale.append(thumb.alt)
        if new_alt is None and not stale:
            return None
        return new_alt, stale

    def print_report(self, changes):
        if not changes:
            self.stdout.write("Brak altów do poprawy.")
            return
        for label, obj, new_alt, stale in changes:
            self.stdout.write(f"{label} #{obj.pk} „{obj.name}”")
            if new_alt is not None:
                self.stdout.write(f"    image_alt: {obj.image_alt!r} -> {new_alt!r}")
            if stale:
                old = ", ".join(sorted({repr(a) for a in stale}))
                self.stdout.write(f"    miniatury ({len(stale)}): alt {old} -> zsynchronizowane")
        self.stdout.write(f"\nRazem: {len(changes)} obiektów.\n")

    def revalidate_frontend(self, changes):
        # Te same funkcje co sygnały post_save (QuerySet.update() ich nie wywołuje).
        from web.articles.signals import revalidate_product_cache_article
        from web.categories.signals import revalidate_product_cache_category
        from web.products.signals import revalidate_product_cache_product

        receivers = {
            Category: revalidate_product_cache_category,
            Product: revalidate_product_cache_product,
            Article: revalidate_product_cache_article,
        }
        for _label, obj, *_rest in changes:
            model = type(obj)
            receivers[model](sender=model, instance=obj)
        self.stdout.write(f"Wysłano rewalidację cache frontendu dla {len(changes)} obiektów.")
