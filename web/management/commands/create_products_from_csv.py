import os

import numpy as np
import pandas as pd
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand

from web.models.categories import Category
from web.models.prices import ProductPrice
from web.models.products import Brand, Product


class Command(BaseCommand):
    help = "Import products from a CSV file and assign them to a specified category."

    def add_arguments(self, parser):
        # Dodajemy dwa argumenty: nazwę pliku i kategorię
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the CSV file with product data.",
        )
        parser.add_argument(
            "category_name",
            type=str,
            help="Category name to assign to the products.",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]  # Pobieramy nazwę pliku
        category_name = options["category_name"]  # Pobieramy nazwę kategorii

        default_brand = Brand.objects.get(name="Expres")

        # Wczytujemy dane z CSV
        try:
            data = pd.read_csv(file_path, index_col=0)
        except FileNotFoundError:
            self.stderr.write(f"File {file_path} not found.")
            return

        df = data.replace({np.nan: None})

        # Znajdujemy kategorię lub tworzymy nową
        category, created = Category.objects.get_or_create(name=category_name)

        if created:
            self.stdout.write(f"Created new category: {category_name}")
        else:
            self.stdout.write(f"Using existing category: {category_name}")

        # Tworzymy produkty
        for index, row in df.iterrows():
            image_path = "DATA/" + row["image_url"]

            # Sprawdzamy, czy plik istnieje
            if not os.path.exists(image_path):
                self.stderr.write(f"Image file {image_path} not found.")
                continue

            # Otwieramy lokalny plik zamiast używać urlopen
            with open(image_path, "rb") as img_file:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(img_file.read())
                img_temp.flush()

                # Tworzymy produkt
                product = Product(
                    name=row["name"],
                    qty=row["qty"],
                    brand=default_brand,
                    category=category,
                    image_alt=row["name"],
                    image_title=row["name"],
                    oryg_image=File(
                        img_temp, name=os.path.basename(image_path)
                    ),
                )
                product.save()

                # Tworzymy cenę dla produktu
                product_price = ProductPrice(
                    product=product, price=row["price"]
                )
                product_price.save()

                self.stdout.write(
                    f"Product {product.name} created with price {product_price.price}"
                )
