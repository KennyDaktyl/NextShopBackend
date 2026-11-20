"""Komenda przebuduj_klucze_samochodowe: podgląd nic nie zapisuje, --apply podmienia
ceny i tworzy nowe strony, drugie uruchomienie niczego nie zmienia, slugi zostają."""

import re
from decimal import Decimal
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from web.management.commands import _car_keys_data as data
from web.models.articles import Article
from web.models.categories import Category
from web.models.heros import Hero
from web.models.prices import ProductPrice
from web.models.products import Product

OLD_BRAND_PRICE = data.REPLACEMENTS[0][3]
OLD_PROG_PRICE = data.REPLACEMENTS[1][3]
OLD_VAG = data.REPLACEMENTS[3][3]


def make(model, **fields):
    obj = model(**fields)
    obj.save()
    return obj


def words(html):
    return len(re.sub(r"<[^>]+>", " ", html).split())


def run(*args):
    out = StringIO()
    call_command("przebuduj_klucze_samochodowe", *args, stdout=out)
    return out.getvalue()


class PrzebudujKluczeSamochodoweTests(TestCase):
    def setUp(self):
        patcher = mock.patch("requests.post")
        patcher.start()
        self.addCleanup(patcher.stop)

        produkty = make(Category, name="Produkty", order=1)
        self.uslugi = make(Category, name="Usługi", order=21)
        make(
            Category,
            name="Pieczątki",
            parent=produkty,
            order=1,
            on_first_page=True,
        )
        make(
            Category,
            name="Klucze",
            parent=produkty,
            order=2,
            on_first_page=True,
        )
        self.car = make(
            Category,
            name="Klucze samochodowe",
            parent=self.uslugi,
            order=20,
            description=data.REPLACEMENTS[8][3],
            seo_text=(
                '<ul><li><a href="x">Programowanie</a> Najczęściej: <a href="/uslugi/klucze-samochodowe/'
                'programowanie-kluczy-samochodowych/programowanie-kluczy-i-pilotow-samochodowych-chevrolet" '
                'class="underline">Chevrolet</a>.</li>\n'
                '    <li><a href="/uslugi/klucze-samochodowe/kopiowanie-immobilizerow" class="underline">'
                "<strong>Kopiowanie</strong></a></li></ul>"
            ),
        )
        self.programming = make(
            Category,
            name="Programowanie Kluczy Samochodowych",
            parent=self.car,
            order=3,
            seo_text=f"<p>Intro</p>\n  {OLD_VAG}\n  <p>{OLD_PROG_PRICE} Dojeżdżam.</p>",
        )
        self.opel = make(
            Category,
            name="Programowanie Kluczy i Pilotów Samochodowych Opel",
            parent=self.programming,
            seo_text=f"<p>{OLD_BRAND_PRICE} Dokładną cenę podam.</p>",
        )
        self.copying = make(
            Category,
            name="Kopiowanie Immobilizerów",
            parent=self.car,
            seo_text=(
                "<p>Kopiowanie wykonuję też w autach grupy VAG (Volkswagen, Skoda, Audi, Seat), BMW i Volvo.</p>"
                "<p>Kopiowanie immobilizera od 150 zł. Usługę wykonuję.</p>"
            ),
        )
        self.mobile = make(
            Category,
            name="Mobilne dorabianie kluczy",
            parent=self.uslugi,
            order=0,
        )
        for name in (
            "Wymiana Obudowy",
            "Wymiana baterii w pilotach samochodowych",
        ):
            make(Category, name=name, parent=self.car)
        for name, order in (
            ("Dorabianie kluczy mieszkaniowych", 1),
            ("Mobilne wyrób pieczątek", 2),
            ("Mobilne kodowanie pilotów do bram", 3),
            ("Naprawy telefonów", 30),
        ):
            make(Category, name=name, parent=self.uslugi, order=order)
        make(Category, name="Piloty do bram", parent=produkty, order=3)

        for slug, name, price, field_values in (
            (
                "klucze-samochodowe-id-643",
                "Klucze samochodowe obudowy",
                "100.00",
                {
                    "description": data.REPLACEMENTS[9][3],
                    "meta_title": data.REPLACEMENTS[10][3],
                    "meta_description": data.REPLACEMENTS[11][3],
                },
            ),
            (
                "immobilizery-i-piloty-id-644",
                "Immobilizery i piloty",
                "300.00",
                {
                    "meta_description": data.REPLACEMENTS[12][3],
                    "description": data.REPLACEMENTS[13][3],
                },
            ),
            (
                "kopiowanie-immobilizerow-id-620",
                "Kopiowanie immobilizerów",
                "250.00",
                {},
            ),
        ):
            product = make(
                Product,
                name=name,
                category=self.mobile,
                is_service=True,
                qty=1,
            )
            Product.objects.filter(pk=product.pk).update(
                slug=slug, **field_values
            )
            make(ProductPrice, product=product, price=Decimal(price))

        article = Article(
            name="Zgubiony kluczyk",
            category=self.car,
            content=f"<p>{OLD_PROG_PRICE} Dokładną cenę podaję.</p>",
        )
        article.save()
        Article.objects.filter(pk=article.pk).update(
            slug="zgubiony-kluczyk-do-auta-dorobienie-klucza-bez-oryginalu-z-dojazdem-id-10"
        )
        self.slugs_before = set(
            Category.objects.values_list("slug", flat=True)
        ) | set(Product.objects.values_list("slug", flat=True))

    def all_texts(self):
        texts = []
        for c in Category.objects.all():
            texts += [
                c.meta_title or "",
                c.meta_description or "",
                c.description or "",
                c.seo_text or "",
            ]
        for p in Product.objects.all():
            texts += [
                p.meta_title or "",
                p.meta_description or "",
                p.description or "",
            ]
        texts += list(Article.objects.values_list("content", flat=True))
        return " ".join(texts)

    def test_dry_run_writes_nothing(self):
        self.assertIn("Tryb podglądu", run())
        self.assertFalse(
            Category.objects.filter(
                slug="awaryjne-otwieranie-samochodow"
            ).exists()
        )
        self.assertIn("od 180 zł", self.all_texts())

    def test_apply_and_idempotency(self):
        output = run("--apply")
        self.assertNotIn("! ", output, output)

        texts = self.all_texts()
        self.assertNotRegex(texts, r"180\s?zł|od 150 zł|8:00|17:00")
        self.assertIn(
            data.PRICE_SENTENCE, Category.objects.get(pk=self.opel.pk).seo_text
        )
        self.assertIn(
            "także roczniki po 2016",
            Category.objects.get(pk=self.programming.pk).seo_text,
        )
        self.assertIn(
            "awaryjne-otwieranie-samochodow",
            Category.objects.get(pk=self.car.pk).seo_text,
        )
        self.assertEqual(
            Product.objects.get(
                slug="kopiowanie-immobilizerow-id-620"
            ).current_price,
            Decimal("300.00"),
        )
        self.assertEqual(
            Product.objects.get(
                slug="klucze-samochodowe-id-643"
            ).current_price,
            Decimal("100.00"),
        )

        emergency = Category.objects.get(slug="awaryjne-otwieranie-samochodow")
        self.assertEqual(
            emergency.get_full_path(),
            "/uslugi/klucze-samochodowe/awaryjne-otwieranie-samochodow",
        )
        self.assertTrue(
            600 <= words(emergency.seo_text) <= 900, words(emergency.seo_text)
        )
        self.assertEqual(emergency.faqs.count(), 4)
        self.assertLessEqual(len(emergency.meta_title), 60)
        self.assertLessEqual(len(emergency.meta_description), 160)

        bodies = []
        for brand in ("audi", "volkswagen", "seat"):
            page = Category.objects.get(
                slug=f"programowanie-kluczy-i-pilotow-samochodowych-{brand}"
            )
            self.assertEqual(page.parent_id, self.programming.pk)
            self.assertTrue(
                400 <= words(page.seo_text) <= 600,
                (brand, words(page.seo_text)),
            )
            self.assertTrue(3 <= page.faqs.count() <= 4)
            self.assertLessEqual(len(page.meta_title), 60)
            self.assertLessEqual(len(page.meta_description), 160)
            self.assertIn("po 2016", page.seo_text)
            # Bez celowo wspólnego bloku ceny/dojazdu na końcu strony.
            body = re.sub(
                r"<[^>]+>",
                " ",
                page.seo_text.split("Cena i obszar dojazdu")[0],
            )
            bodies.append(
                {
                    s.strip()
                    for s in re.split(r"[.!?]", body)
                    if len(s.split()) > 4
                }
            )
        # Treści marek nie są kopią z podmienioną nazwą: wspólne może być najwyżej zdanie o urządzeniu VAG.
        for i in range(3):
            for j in range(i + 1, 3):
                shared = bodies[i] & bodies[j]
                self.assertLessEqual(len(shared), 1, shared)

        promoted = list(
            Category.objects.filter(
                slug__in=[
                    "klucze-samochodowe",
                    "uslugi",
                    "mobilne-kodowanie-pilotow-do-bram",
                    "piloty-do-bram",
                    "naprawy-telefonow",
                    "klucze",
                    "pieczatki",
                ]
            )
            .order_by("order", "name")
            .values_list("slug", flat=True)
        )
        self.assertEqual(
            promoted,
            [
                "klucze-samochodowe",
                "uslugi",
                "mobilne-kodowanie-pilotow-do-bram",
                "piloty-do-bram",
                "naprawy-telefonow",
                "klucze",
                "pieczatki",
            ],
        )
        mobile = Category.objects.get(pk=self.mobile.pk)
        self.assertTrue(
            mobile.h1_tag.startswith(
                "Dorabianie kluczy samochodowych i mieszkaniowych"
            )
        )

        # Żaden istniejący slug się nie zmienił.
        slugs_after = set(
            Category.objects.values_list("slug", flat=True)
        ) | set(Product.objects.values_list("slug", flat=True))
        self.assertTrue(self.slugs_before <= slugs_after)

        self.assertIn("Liczba zmian: 0", run("--apply"))
