import pandas as pd
from django.core.management.base import BaseCommand
from web.models.products import Product

class Command(BaseCommand):
    help = "Update CSV with product links fetched from the database"

    def handle(self, *args, **options):
        # Ścieżki do plików CSV
        input_file = 'DATA/product_old_links.csv'
        output_file = 'DATA/redirect_links.csv'

        # Wczytanie pliku CSV z kolumnami old_link i slug
        df = pd.read_csv(input_file)

        # Inicjalizacja nowej kolumny na nowe linki
        df['new_link'] = None

        # Iteracja po każdym wierszu i pobieranie nowego linku z bazy na podstawie sluga
        for index, row in df.iterrows():
            slug = row['slug']
            try:
                # Znalezienie produktu na podstawie sluga
                product = Product.objects.filter(slug__icontains=slug).first()
                if product:
                    # Pobranie linku produktu
                    new_link = product.full_path
                    # Zapisanie nowego linku w DataFrame
                    df.at[index, 'new_link'] = new_link
            except Product.DoesNotExist:
                # Jeśli produkt nie istnieje, ostrzeżenie w konsoli i zostawienie pustej wartości
                self.stdout.write(self.style.WARNING(f"Product with slug '{slug}' not found in the database"))

        # Zapisanie zaktualizowanego pliku CSV z nowymi linkami
        df.to_csv(output_file, index=False)

        self.stdout.write(self.style.SUCCESS(f"Successfully updated links and saved to {output_file}"))
