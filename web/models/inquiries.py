from django.db import models


def key_photo_upload_path(instance, filename):
    return f"key_photo_inquiries/{filename}"


class KeyPhotoInquiry(models.Model):
    photo = models.ImageField(
        upload_to=key_photo_upload_path, verbose_name="Zdjęcie klucza"
    )
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    note = models.TextField(verbose_name="Notatka", blank=True)
    created_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Data zgłoszenia"
    )
    handled = models.BooleanField(
        verbose_name="Obsłużone", default=False
    )

    class Meta:
        verbose_name = "Zgłoszenie zdjęcia klucza"
        verbose_name_plural = "Zgłoszenia zdjęć kluczy"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.email} — {self.created_date:%Y-%m-%d %H:%M}"
