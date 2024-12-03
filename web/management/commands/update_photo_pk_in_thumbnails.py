import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from web.models.images import Photo, Thumbnail
from urllib.parse import urlparse


class Command(BaseCommand):
    help = "Aktualizuje relacje Thumbnail.photo na podstawie Photo.thumbnails."

    def handle(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        updated_count = 0
        not_found_count = 0

        self.stdout.write(self.style.SUCCESS("Rozpoczynam aktualizację Thumbnail.photo..."))

        with transaction.atomic():
            thumbnails = Thumbnail.objects.all()
            for thumbnail in thumbnails:
                thumbnail_url = urlparse(thumbnail.oryg_image.url).path
                matching_photo = None

                for photo in Photo.objects.exclude(thumbnails__isnull=True):
                    for size, url in photo.thumbnails.items():
                        if urlparse(url).path == thumbnail_url:
                            matching_photo = photo
                            break

                if matching_photo:
                    thumbnail.photo_pk = matching_photo
                    thumbnail.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Dopasowano Thumbnail ID: {thumbnail.id} do Photo ID: {matching_photo.id}")
                    )
                else:
                    not_found_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"Nie znaleziono dopasowania dla Thumbnail ID: {thumbnail.id}")
                    )

        self.stdout.write(self.style.SUCCESS(f"Zaktualizowano {updated_count} miniatur."))
        self.stdout.write(self.style.WARNING(f"Nie znaleziono dopasowania dla {not_found_count} miniatur."))
