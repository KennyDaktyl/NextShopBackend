import os

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify

from web.models.images import generate_thumbnails


class Payment(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    slug = models.SlugField(max_length=255, blank=True, null=True)
    order = models.IntegerField(verbose_name="Kolejność", default=0)
    price = models.DecimalField(
        max_digits=10, verbose_name="Cena", decimal_places=2
    )
    price_promo = models.DecimalField(
        max_digits=10,
        verbose_name="Cena promocyjna",
        decimal_places=2,
        default=0,
    )
    payment_on_delivery = models.BooleanField(
        verbose_name="Czy to płatność przy odbiorze?", default=False
    )
    payment_online = models.BooleanField(
        verbose_name="Czy to płatność online?", default=False
    )
    bank_transfer = models.BooleanField(
        verbose_name="Czy to przelew bankowy?", default=False
    )
    payment_deferral = models.IntegerField(
        verbose_name="Dni na opłacenie", default=14
    )

    oryg_image = models.ImageField(
        verbose_name="Zdjęcie główne", upload_to="deliveries", blank=True
    )
    image_alt = models.CharField(
        verbose_name="Tekst alternatywny",
        max_length=255,
        blank=True,
        null=True,
    )
    image_title = models.CharField(
        verbose_name="Tytuł zdjęcia", max_length=255, blank=True, null=True
    )
    thumbnails = models.JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(verbose_name="Czy aktywna?", default=True)

    class Meta:
        verbose_name = "Rodzaj płatności"
        verbose_name_plural = "Rodzaje płatności"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name + f" - {self.price} zł"

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None

        if not self.oryg_image:
            self.thumbnails = {}

        if self.pk:
            old_delivery = Payment.objects.get(pk=self.pk)
            old_image = old_delivery.oryg_image

        if old_name != self.name:
            self.slug = slugify(self.name)

        if old_image and old_image != self.oryg_image:
            thumbs = self.payment_thumbnails.filter(main=True)
            if thumbs:
                thumbs.delete()

        super().save(*args, **kwargs)
        if is_new_instance or old_image != self.oryg_image and self.oryg_image:
            if self.oryg_image:
                self.thumbnails = generate_thumbnails(
                    self,
                    True,
                    False,
                    "payment",
                    self.oryg_image,
                    alt=self.image_alt,
                    title=self.image_title,
                )
        super().save()

    @property
    def image(self):
        return self.payment_thumbnails.filter(
            width_expected=100, height_expected=100
        ).first()

    def get_full_image_url(self, request):
        if self.oryg_image:
            return request.build_absolute_uri(
                settings.MEDIA_URL + self.oryg_image.url
            )
        return ""


@receiver(models.signals.pre_save, sender=Payment)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Payment.objects.get(pk=instance.pk).oryg_image
        new_file = instance.oryg_image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Payment.DoesNotExist:
        return False

    except Payment.DoesNotExist:
        return False


@receiver(models.signals.post_delete, sender=Payment)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.oryg_image:
        if os.path.isfile(instance.oryg_image.path):
            os.remove(instance.oryg_image.path)
