"""Komenda ujednolic_tresci_seo: podgląd nic nie zapisuje, --apply zapisuje,
drugie uruchomienie niczego już nie zmienia."""

from decimal import Decimal
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from web.management.commands.ujednolic_tresci_seo import (
    LOCATION,
    LOCATION_SHORT,
)
from web.models.articles import Article
from web.models.categories import Category, ServiceLocality
from web.models.prices import ProductPrice
from web.models.products import Product

LONG_META = (
    "Dorabianie kluczy mieszkaniowych od 15 zł na miejscu, szybko i solidnie. "
    "Zapraszamy: Rybna i okolice. Klucze do skrzynek."
)


def make(model, **fields):
    # save() modeli z miniaturami woła super().save() dwa razy – objects.create() (force_insert) się wysypuje.
    obj = model(**fields)
    obj.save()
    return obj


class UjednolicTresciSeoTests(TestCase):
    def setUp(self):
        patcher = mock.patch("requests.post")
        self.requests_post = patcher.start()
        self.addCleanup(patcher.stop)

        uslugi = make(
            Category,
            name="Usługi",
            meta_description="Usługi – Kraków i okolice.",
        )
        self.keys = make(
            Category,
            name="Dorabianie kluczy mieszkaniowych",
            parent=uslugi,
            meta_description=LONG_META,
            description="Dorabiamy klucze od 15,00 zł. Obsługujemy gminy Czernichów, Liszki, Krzeszowice, Alwernia.",
        )
        # Nawet ze skróconą frazą > 160 znaków -> pominięte z ostrzeżeniem.
        self.too_long = make(
            Category,
            name="Klucze zabezpieczone",
            parent=uslugi,
            meta_description="Klucze " + "x" * 120 + " Rybna i okolice.",
        )
        self.key_service = make(
            Product,
            name="Dorobienie klucza mieszkaniowego",
            category=self.keys,
            is_service=True,
            meta_description="Klucz mieszkaniowy od 15zł – Rybna i okolice.",
            description="<p>Dorobienie klucza od 15 zł.</p>",
            seo_text="Cena od 15 zł za sztukę.",
        )
        self.old_price = ProductPrice.objects.create(
            product=self.key_service, price=Decimal("15.00")
        )
        self.ok_price = ProductPrice.objects.create(
            product=self.key_service, price=Decimal("25.00")
        )

        shop = make(Category, name="Sklep")
        self.shop_product = make(
            Product,
            name="Breloczek",
            category=shop,
            is_service=False,
            meta_description="Breloczek od 15 zł – Rybna i okolice.",
            description="Breloczek od 15 zł.",
        )
        self.shop_price = ProductPrice.objects.create(
            product=self.shop_product, price=Decimal("10.00")
        )

        self.privacy = make(
            Article,
            name="Polityka prywatności",
            slug="polityka-prywatnosci",
            category=uslugi,
            content="Usługi od 15 zł, Rybna i okolice.",
        )
        self.article = make(
            Article,
            name="Ile kosztuje klucz",
            slug="ile-kosztuje-klucz",
            category=uslugi,
            meta_description="Klucz od 15 zł.",
            content="Klucz mieszkaniowy dorobimy od 15 zł.",
        )

        ServiceLocality.objects.all().delete()  # seed z migracji 0125
        ServiceLocality.objects.create(
            name="Krzeszowice",
            slug="krzeszowice",
            region_label="Gmina Krzeszowice",
            local_note="x",
            order=1,
        )
        ServiceLocality.objects.create(
            name="Krowodrza",
            slug="krowodrza",
            region_label="Kraków – Krowodrza",
            local_note="x",
            order=2,
        )
        ServiceLocality.objects.create(
            name="Alwernia",
            slug="alwernia",
            region_label="Gmina Alwernia",
            local_note="x",
            order=3,
        )
        ServiceLocality.objects.create(
            name="Ukryta",
            slug="ukryta",
            region_label="Gmina X",
            local_note="x",
            order=4,
            is_active=False,
        )

        self.requests_post.reset_mock()

    def run_command(self, *args):
        out = StringIO()
        with self.captureOnCommitCallbacks(execute=True):
            call_command("ujednolic_tresci_seo", *args, stdout=out)
        return out.getvalue()

    def snapshot(self):
        return {
            "categories": list(Category.objects.order_by("id").values()),
            "products": list(Product.objects.order_by("id").values()),
            "prices": list(ProductPrice.objects.order_by("id").values()),
            "articles": list(Article.objects.order_by("id").values()),
        }

    def test_dry_run_lists_changes_and_saves_nothing(self):
        before = self.snapshot()
        output = self.run_command()

        self.assertEqual(self.snapshot(), before)
        self.assertIn("Tryb podglądu", output)
        self.assertIn(f"[Product #{self.key_service.pk}", output)
        self.assertIn(f"[ProductPrice #{self.old_price.pk}", output)
        self.assertIn(
            f"Category #{self.too_long.pk} meta_description", output
        )  # ostrzeżenie
        self.requests_post.assert_not_called()

    def test_apply_saves_changes(self):
        self.run_command("--apply")
        sentence = "Dojeżdżamy m.in. do: Krzeszowice, Alwernia oraz dzielnic Krakowa: Krowodrza."

        self.old_price.refresh_from_db()
        self.ok_price.refresh_from_db()
        self.assertEqual(self.old_price.price, Decimal("20.00"))
        self.assertEqual(self.ok_price.price, Decimal("25.00"))

        self.key_service.refresh_from_db()
        self.assertEqual(
            self.key_service.meta_description,
            f"Klucz mieszkaniowy od 20 zł – {LOCATION}.",
        )
        self.assertEqual(
            self.key_service.description,
            f"<p>Dorobienie klucza od 20 zł.</p>\n<p>{sentence}</p>",
        )
        self.assertEqual(self.key_service.seo_text, "Cena od 20 zł za sztukę.")

        self.keys.refresh_from_db()
        self.assertEqual(
            self.keys.description,
            f"Dorabiamy klucze od 20 zł. Obsługujemy {LOCATION}. {sentence}",
        )
        # Pełna fraza przekroczyłaby 160 znaków -> wersja skrócona.
        self.assertIn(LOCATION_SHORT, self.keys.meta_description)
        self.assertLessEqual(len(self.keys.meta_description), 160)

        self.article.refresh_from_db()
        self.assertEqual(
            self.article.content, "Klucz mieszkaniowy dorobimy od 20 zł."
        )
        self.assertEqual(self.article.meta_description, "Klucz od 20 zł.")

        # Nie-usługi i dokumenty prawne bez zmian.
        self.shop_product.refresh_from_db()
        self.shop_price.refresh_from_db()
        self.privacy.refresh_from_db()
        self.assertEqual(
            self.shop_product.meta_description,
            "Breloczek od 15 zł – Rybna i okolice.",
        )
        self.assertEqual(self.shop_price.price, Decimal("10.00"))
        self.too_long.refresh_from_db()
        self.assertTrue(
            self.too_long.meta_description.endswith(" Rybna i okolice.")
        )
        self.assertEqual(
            self.privacy.content, "Usługi od 15 zł, Rybna i okolice."
        )

        self.assertTrue(self.requests_post.called)

    def test_second_run_changes_nothing(self):
        self.run_command("--apply")
        after_first = self.snapshot()
        self.requests_post.reset_mock()

        output = self.run_command("--apply")

        self.assertIn("Brak zmian", output)
        self.assertEqual(self.snapshot(), after_first)
        self.requests_post.assert_not_called()
