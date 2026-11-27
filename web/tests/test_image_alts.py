"""Strona główna: tylko podkategorie 1. poziomu. Alt zdjęć: zmiana w adminie trafia do
miniatur, pusty/techniczny alt zastępuje nazwa, komenda fix_image_alts (--dry-run nic nie zapisuje)."""

import shutil
import tempfile
from io import BytesIO, StringIO
from unittest import mock

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from web.categories.serializers import CategoryListOnFirstPageSerializer
from web.models.articles import Article
from web.models.categories import Category
from web.models.images import is_technical_alt

MEDIA = tempfile.mkdtemp(prefix="image_alts_media_")


def make(model, **fields):
    obj = model(**fields)
    obj.save()
    return obj


def png():
    buf = BytesIO()
    Image.new("RGB", (40, 60), "black").save(buf, "PNG")
    return ContentFile(buf.getvalue())


def with_image(model, **fields):
    obj = model(**fields)
    obj.oryg_image.save("zdjecie.png", png(), save=False)
    obj.save()
    return obj


def alts(obj):
    return set(obj.main_thumbnails.values_list("alt", flat=True))


@override_settings(MEDIA_ROOT=MEDIA)
class ImageAltTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        patcher = mock.patch("requests.post")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_first_page_subcategories_without_grandchildren(self):
        root = make(Category, name="Usługi zbiorcze", on_first_page=True)
        second = make(Category, name="A druga", parent=root, order=2)
        first = make(Category, name="Z pierwsza", parent=root, order=1)
        make(Category, name="Ukryta", parent=root, order=3, is_active=False)
        make(Category, name="Wnuk marki", parent=first)

        data = CategoryListOnFirstPageSerializer(root).data
        names = [c["name"] for c in data["all_subcategories"]]
        self.assertEqual(names, [first.name, second.name])

    def test_is_technical_alt(self):
        for alt in (None, "", "  ", "Category Image", "Thumbnail", "Large Image",
                    "dorabianie-kluczy-samochodowych-krakow-id-7", "pilot-do-bramy", "foto.webp"):
            self.assertTrue(is_technical_alt(alt), alt)
        for alt in ("Pilot do bramy – Kraków", "Klucz", "Skoda Octavia"):
            self.assertFalse(is_technical_alt(alt), alt)

    def test_alt_change_without_new_image_reaches_thumbnails(self):
        cat = with_image(Category, name="Mobilne kodowanie pilotów do bram")
        self.assertEqual(alts(cat), {cat.name})  # pusty alt -> nazwa

        cat.image_alt = "Pilot do bramy programowany z dojazdem – Kraków"
        cat.image_title = "Pilot do bramy"
        cat.save()
        self.assertEqual(alts(cat), {cat.image_alt})
        self.assertEqual(set(cat.main_thumbnails.values_list("title", flat=True)), {"Pilot do bramy"})
        self.assertEqual(cat.main_thumbnails.count(), 3)  # bez nowych plików

    def test_article_slug_alt_replaced_by_name(self):
        article = with_image(
            Article,
            name="Dorabianie kluczy samochodowych z dojazdem",
            category=make(Category, name="Blog"),
            content="Treść",
            image_alt="dorabianie-kluczy-samochodowych-z-dojazdem-id-7",
        )
        self.assertEqual(alts(article), {article.name})

    def test_fix_image_alts_command(self):
        cat = with_image(Category, name="Klucze Samochodowe")
        # Stan jak na produkcji: techniczny alt w polu i w miniaturach.
        Category.objects.filter(pk=cat.pk).update(image_alt="Category Image")
        cat.main_thumbnails.update(alt="Category Image")

        out = StringIO()
        call_command("fix_image_alts", "--dry-run", stdout=out)
        self.assertIn("'Category Image' -> 'Klucze Samochodowe'", out.getvalue())
        cat.refresh_from_db()
        self.assertEqual(cat.image_alt, "Category Image")
        self.assertEqual(alts(cat), {"Category Image"})

        call_command("fix_image_alts", stdout=StringIO())
        cat.refresh_from_db()
        self.assertEqual(cat.image_alt, "Klucze Samochodowe")
        self.assertEqual(alts(cat), {"Klucze Samochodowe"})

        out = StringIO()
        call_command("fix_image_alts", "--dry-run", stdout=out)
        self.assertIn("Brak altów do poprawy", out.getvalue())
