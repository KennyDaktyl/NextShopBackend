import numpy as np
import pandas as pd
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from web.models.accounts import Profile


class Command(BaseCommand):
    help = "Import products from a CSV file and assign them to a specified category."

    def handle(self, *args, **options):
        file_path = "DATA/users.csv"  # Pobieramy nazwę pliku

        try:
            data = pd.read_csv(file_path, index_col=0)
        except FileNotFoundError:
            self.stderr.write(f"File {file_path} not found.")
            return

        df = data.replace({np.nan: None})

        # Tworzymy usera
        for index, row in df.iterrows():
            print(row)
            first_name = row["first_name"] if row["first_name"] else ""
            last_name = row["last_name"] if row["last_name"] else ""
            user, created = User.objects.get_or_create(
                username=row["username"],
                email=row["username"],
                first_name=first_name,
                last_name=last_name,
                defaults={
                    "password": row["password"]
                },  # Ustawiamy hasło tylko dla nowych użytkowników
            )

            # Sprawdzenie istnienia profilu na podstawie usera

            profile, created = Profile.objects.get_or_create(
                user=user,  # Szukamy po polu 'user'
                defaults={
                    "mobile": row["mobile"],
                    "street": row["street"],
                    "house_number": row["house"],
                    "local_number": row["door"],
                    "city": row["city"],
                    "postal_code": row["post_code"]
                    .strip()
                    .replace(" ", "")
                    .replace("-", ""),
                },
            )

            make_invoice = row["company"]
            if make_invoice:
                profile.make_invoice = make_invoice
                profile.company = row["company_name"]
                profile.company_payer = row["company_peyer"]

                # Oczyszczamy NIP i inne pola związane z fakturą
                profile.nip = (
                    row["nip"].strip().replace("-", "").replace(" ", "")
                )
                profile.invoice_street = row["street"]
                profile.invoice_house_number = row["house"].strip()
                profile.invoice_local_number = row["door"]
                profile.invoice_city = row["city"]

                # Oczyszczamy kod pocztowy do faktury
                invoice_postal_code = (
                    row["post_code"].strip().replace(" ", "").replace("-", "")
                )
                if len(invoice_postal_code) > 6:
                    self.stderr.write(
                        f"Error: Invoice postal code too long for user {user.username}: {invoice_postal_code}"
                    )
                else:
                    profile.invoice_postal_code = invoice_postal_code

                profile.save()

            self.stdout.write(
                f"Profile {user.username} created with profile {profile.make_invoice}"
            )
