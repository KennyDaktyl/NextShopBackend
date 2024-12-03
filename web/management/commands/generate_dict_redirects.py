import pandas as pd
from django.core.management.base import BaseCommand
from web.models.products import Product

class Command(BaseCommand):
    help = "Generate Next.js redirects configuration for products"

    def handle(self, *args, **options):
        # Ścieżki do pliku CSV i wyjściowego pliku konfiguracyjnego
        input_file = 'DATA/redirect_links.csv'
        output_file = 'DATA/next.config.js'

        # Wczytanie pliku CSV
        df = pd.read_csv(input_file)

        # Inicjalizacja listy na przekierowania
        redirects = []

        # Iteracja po każdym wierszu pliku CSV
        for index, row in df.iterrows():
            old_link = row['old_link']
            new_link = row.get('new_link', None)  # Pobierz new_link, jeśli istnieje, inaczej None
            
            if pd.notna(new_link):  # Jeśli new_link nie jest pusty
                # Tworzymy przekierowanie dla istniejącego nowego linku
                redirect_entry = {
                    'source': old_link,
                    'destination': new_link,
                    'permanent': True
                }
                redirects.append(redirect_entry)
            else:
                # Jeśli new_link jest pusty, tworzymy regułę 410
                redirect_entry = {
                    'source': old_link,
                    'destination': '/410',
                    'statusCode': 410
                }
                redirects.append(redirect_entry)

        # Generowanie pliku next.config.js
        with open(output_file, 'w') as f:
            f.write("module.exports = {\n")
            f.write("  async redirects() {\n")
            f.write("    return [\n")

            # Zapisujemy każdy wpis przekierowania do pliku
            for redirect in redirects:
                if 'permanent' in redirect:
                    f.write(f"      {{ source: '{redirect['source']}', destination: '{redirect['destination']}', permanent: true }},\n")
                else:
                    f.write(f"      {{ source: '{redirect['source']}', destination: '{redirect['destination']}', statusCode: {redirect['statusCode']} }},\n")

            f.write("    ];\n")
            f.write("  },\n")
            f.write("};\n")

        self.stdout.write(self.style.SUCCESS(f'Successfully generated Next.js redirects configuration and saved to {output_file}'))

