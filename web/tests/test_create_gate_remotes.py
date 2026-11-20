"""Komenda create_gate_remotes: podgląd nic nie zapisuje, --apply tworzy kategorię
i 13 pilotów z własnymi plikami zdjęć, ponowne uruchomienie nic nie zmienia,
a pozycje usługowe zostają nietknięte."""

import os
import re
import shutil
import tempfile
from decimal import Decimal
from io import BytesIO, StringIO
from unittest import mock

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from PIL import Image

from web.management.commands import _gate_remotes_data as data
from web.models.categories import Category
from web.models.images import Photo, Thumbnail
from web.models.prices import ProductPrice
from web.models.products import Brand, Product, ProductFAQ, ProductSpecification

MEDIA = tempfile.mkdtemp(prefix="gate_remotes_media_")


def make(model, **fields):
    obj = model(**fields)
    obj.save()
    return obj


def png(color="black"):
    buf = BytesIO()
    Image.new("RGB", (40, 60), color).save(buf, "PNG")
    return ContentFile(buf.getvalue())


def run(*args):
    out = StringIO()
    call_command("create_gate_remotes", *args, stdout=out)
    return out.getvalue()


@override_settings(MEDIA_ROOT=MEDIA)
class CreateGateRemotesTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        patcher = mock.patch("requests.post")
        patcher.start()
        self.addCleanup(patcher.stop)

        self.produkty = make(Category, name="Produkty")
        uslugi = make(Category, name="Usługi")
        self.service_cat = make(
            Category, name="Mobilne kodowanie pilotów do bram", parent=uslugi
        )
        self.zamiennik = make(Brand, name="Zamiennik")
        self.hormann = make(Brand, name="Hormann")

        # Product.save() zakłada, że obiekt z pk już istnieje – nie da się nadać id 652–664,
        # więc podmieniamy service_id w danych na id utworzonych usług.
        self.services = {}
        remotes = []
        for remote in data.REMOTES:
            service = Product(
                name=f"Pilot bramowy {remote['label']} usługa",
                category=self.service_cat,
                is_service=True,
                qty=1,
                description="Usługa kompleksowa: pilot + kodowanie + dojazd. Cena: 199 zł.",
            )
            service.oryg_image.save(f"svc-{remote['service_id']}.png", png(), save=False)
            service.save()
            make(ProductPrice, product=service, price=Decimal("199.00"))
            remotes.append({**remote, "service_id": service.pk})
            self.services[service.pk] = service
        remotes_patch = mock.patch.object(data, "REMOTES", remotes)
        remotes_patch.start()
        self.addCleanup(remotes_patch.stop)
        self.remotes = remotes
        self.came_space = next(r for r in remotes if r["sku"] == "PB-CAME-025")["service_id"]
        self.smilo_service = next(r for r in remotes if r["sku"] == "PB-NICE-SMILO-002")["service_id"]
        for alt in ("Pilot bramowy Came 025 z opakowaniem", "Pilot bramowy Came 025 - widok z bliska"):
            photo = Photo(product=self.services[self.came_space], name=alt, image_alt=alt)
            photo.oryg_image.save("svc-photo.png", png("white"), save=False)
            photo.save()

        self.service_snapshot = self.snapshot_services()

    def snapshot_services(self):
        return list(
            Product.objects.filter(is_service=True)
            .order_by("id")
            .values("id", "name", "slug", "description", "category_id", "oryg_image", "brand_id")
        ) + [list(ProductPrice.objects.filter(product__is_service=True).values_list("price", flat=True))]

    def gate_products(self):
        return Product.objects.filter(category__slug="piloty-do-bram")

    def test_dry_run_writes_nothing(self):
        output = run()
        self.assertIn("Tryb podglądu", output)
        self.assertFalse(Category.objects.filter(slug="piloty-do-bram").exists())
        self.assertEqual(Product.objects.filter(is_service=False).count(), 0)
        self.assertEqual(Brand.objects.get(pk=self.hormann.pk).name, "Hormann")

    def test_apply_creates_category_brands_and_products(self):
        run("--apply")

        category = Category.objects.get(slug="piloty-do-bram")
        self.assertEqual(category.parent, self.produkty)
        self.assertEqual(category.get_full_path(), "/produkty/piloty-do-bram")
        self.assertEqual(category.h1_tag, "Piloty do bram garażowych i wjazdowych")
        self.assertIn('href="/uslugi/mobilne-kodowanie-pilotow-do-bram"', category.seo_text)
        self.assertIn("pilot do bramy z dojazdem i programowaniem", category.seo_text)
        seo_words = len(re.sub(r"<[^>]+>", " ", category.seo_text).split())
        self.assertTrue(150 <= seo_words <= 250, seo_words)

        hormann = Brand.objects.get(pk=self.hormann.pk)
        self.assertEqual((hormann.name, hormann.slug), ("Hörmann", "hormann"))
        self.assertEqual(
            set(Brand.objects.exclude(slug=None).values_list("name", flat=True)),
            {"Nice", "CAME", "FAAC", "BFT", "Beninca", "Somfy", "Hörmann"},
        )

        products = self.gate_products()
        self.assertEqual(products.count(), 13)
        for remote in self.remotes:
            p = products.get(sku=remote["sku"])
            self.assertEqual(p.slug, remote["slug"])
            self.assertEqual(p.full_path, f"/produkt/{remote['slug']}")
            self.assertFalse(p.is_service)
            self.assertEqual(p.qty, 1)
            self.assertEqual(p.current_price, Decimal("69.00"))
            self.assertIsNone(p.brand_id)  # marka dopiero po potwierdzeniu oryginalności
            self.assertEqual(p.compatible_brand.slug, remote["compatible"])
            self.assertEqual(p.gtin, "")
            self.assertLessEqual(len(p.meta_title), 60)
            self.assertTrue(140 <= len(p.meta_description) <= 155, p.meta_description)
            self.assertIn("69 zł", p.meta_title)
            words = len(re.sub(r"<[^>]+>", " ", p.seo_text).split())
            self.assertTrue(250 <= words <= 400, (p.slug, words))
            self.assertIn(f"Z jakimi napędami współpracuje {remote['label']}", p.seo_text)
            self.assertIn(
                f"zaprogramuję pilota {p.compatible_brand.name} u Ciebie na miejscu", p.seo_text
            )
            # Nowy plik, nie współdzielony z usługą.
            self.assertTrue(p.oryg_image.name.startswith(f"products/{remote['slug']}"))
            self.assertNotEqual(p.oryg_image.name, self.services[remote["service_id"]].oryg_image.name)
            thumbs = Thumbnail.objects.filter(product=p, main=True)
            self.assertEqual(thumbs.count(), 3)
            self.assertTrue(all(t.alt == p.image_alt for t in thumbs))
            self.assertEqual(p.specifications.count(), len(remote["specs"]))
            self.assertTrue(4 <= p.faqs.count() <= 6)

        space = products.get(sku="PB-CAME-025")
        self.assertEqual(space.photos.count(), 2)
        self.assertNotIn("svc-photo", "".join(space.photos.values_list("oryg_image", flat=True)))

        self.assertEqual(self.snapshot_services(), self.service_snapshot)

    def test_second_run_is_idempotent(self):
        run("--apply")
        counts = (
            Product.objects.count(),
            ProductPrice.objects.count(),
            Thumbnail.objects.count(),
            Photo.objects.count(),
            ProductFAQ.objects.count(),
            ProductSpecification.objects.count(),
            Brand.objects.count(),
            Category.objects.count(),
        )
        output = run("--apply")
        self.assertIn("Liczba zmian: 0", output)
        self.assertEqual(
            counts,
            (
                Product.objects.count(),
                ProductPrice.objects.count(),
                Thumbnail.objects.count(),
                Photo.objects.count(),
                ProductFAQ.objects.count(),
                ProductSpecification.objects.count(),
                Brand.objects.count(),
                Category.objects.count(),
            ),
        )

    def test_rerun_after_price_change_updates_texts_but_keeps_price_and_qty(self):
        run("--apply")
        p = self.gate_products().get(sku="PB-NICE-SMILO-002")
        make(ProductPrice, product=p, price=Decimal("79.00"))
        Product.objects.filter(pk=p.pk).update(qty=5)

        run("--apply")
        p.refresh_from_db()
        self.assertEqual(p.current_price, Decimal("79.00"))
        self.assertEqual(p.qty, 5)
        self.assertIn("79 zł", p.meta_title)
        self.assertIn("79 zł", p.image_title)
        self.assertTrue(p.faqs.filter(question__contains="79 zł").exists())
        self.assertTrue(
            Thumbnail.objects.filter(product=p, main=True, title=p.image_title).exists()
        )
        # Cena „od” w kategorii to minimum – nadal 69 zł z innych pilotów.
        self.assertIn("od 69 zł", Category.objects.get(slug="piloty-do-bram").meta_description)

    def test_refuses_slug_owned_by_service(self):
        Product.objects.filter(pk=self.smilo_service).update(slug="pilot-nice-smilo")
        with self.assertRaisesMessage(Exception, "należy do usługi"):
            run("--apply")
        self.assertFalse(Category.objects.filter(slug="piloty-do-bram").exists())

    def test_api_exposes_new_fields(self):
        run("--apply")
        response = self.client.get("/api/products/pilot-faac-xt4-868-slh-lr/")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["sku"], "PB-FAAC-XT4-868")
        self.assertIsNone(body["brand"])
        self.assertEqual(body["compatible_brand"]["name"], "FAAC")
        self.assertIn({"name": "Częstotliwość", "value": "868,35 MHz"}, body["specifications"])
        self.assertTrue(body["faqs"][0]["question"].startswith("Jak dodać pilot FAAC XT4"))
        self.assertEqual(
            [c["name"] for c in body["category"]["breadcrumbs"]], ["Produkty", "Piloty do bram"]
        )
        listing = self.client.get("/api/categories/category-products/piloty-do-bram/").json()
        self.assertEqual(listing["count"], 13)
        self.assertEqual(listing["results"][0]["qty"], 1)
        self.assertTrue(listing["results"][0]["short_description"])

    def assert_no_replacement_word(self):
        for p in self.gate_products():
            texts = [p.name, p.h1_tag, p.slug, p.meta_title, p.meta_description, p.description,
                     p.short_description, p.seo_text, p.image_alt, p.image_title, p.oryg_image.name]
            texts += list(p.faqs.values_list("question", flat=True)) + list(p.faqs.values_list("answer", flat=True))
            texts += [f"{n} {v}" for n, v in p.specifications.values_list("name", "value")]
            texts += [f"{t.oryg_image.name} {t.alt} {t.title}" for t in Thumbnail.objects.filter(product=p)]
            texts += [f"{ph.oryg_image.name} {ph.image_alt} {ph.slug}" for ph in p.photos.all()]
            for text in texts:
                self.assertNotRegex(text or "", r"(?i)zamiennik|nieoryginal|oryginaln", p.sku)
        category = Category.objects.get(slug="piloty-do-bram")
        for text in (category.meta_title, category.meta_description, category.description, category.seo_text):
            self.assertNotRegex(text, r"(?i)zamiennik|oryginaln")

    def test_no_replacement_wording(self):
        run("--apply")
        self.assert_no_replacement_word()

    def test_rename_from_previous_slugs_and_files(self):
        # Stan po pierwszym wdrożeniu: slugi i pliki z „-zamiennik”.
        old = [{**r, "slug": f"{r['slug']}-zamiennik", "name": f"{r['name']} – zamiennik",
                "label": f"{r['label']} zamiennik"} for r in self.remotes]
        with mock.patch.object(data, "REMOTES", old):
            run("--apply")
        space = self.gate_products().get(sku="PB-CAME-025")
        old_files = [space.oryg_image.path] + [ph.oryg_image.path for ph in space.photos.all()]
        old_files += [t.oryg_image.path for t in Thumbnail.objects.filter(product=space)]
        counts = (Product.objects.count(), ProductPrice.objects.count())

        output = run("--apply")
        self.assertIn("Zapisano", output)
        self.assertEqual(counts, (Product.objects.count(), ProductPrice.objects.count()))
        self.assert_no_replacement_word()
        space.refresh_from_db()
        self.assertEqual(space.slug, "pilot-came-space")
        self.assertEqual(space.photos.count(), 2)
        self.assertEqual(Thumbnail.objects.filter(product=space).count(), 9)  # 3 rozmiary x 3 zdjęcia
        for path in old_files:
            self.assertFalse(os.path.exists(path), path)
        self.assertIn("Liczba zmian: 0", run("--apply"))
