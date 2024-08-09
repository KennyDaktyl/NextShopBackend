import os

from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify

from web.models.images import delete_thumbnails, generate_thumbnails


class Hero(models.Model):
    title = models.CharField(max_length=100, verbose_name="Tytuł")
    slug = models.SlugField(
        max_length=100, verbose_name="Slug", blank=True, null=True
    )
    description = models.TextField(verbose_name="Opis")
    oryg_image = models.ImageField(
        verbose_name="Zdjęcie", upload_to="heros", blank=True, null=True
    )
    link = models.URLField(verbose_name="Link", blank=True, null=True)
    order = models.IntegerField(verbose_name="Kolejność", default=1)
    thumbnails = models.JSONField(default=dict, blank=True, null=True)

    is_active = models.BooleanField(verbose_name="Czy aktywny", default=True)

    class Meta:
        verbose_name = "Hero"
        verbose_name_plural = "Heroy"
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None

        if self.pk:
            if not self.oryg_image:
                self.thumbnails = {}
            old_hero = Hero.objects.get(pk=self.pk)
            old_name = old_hero.title
            old_image = old_hero.image

            if old_hero.oryg_image != self.oryg_image:
                delete_thumbnails(self, "hero")

            if old_hero.image and old_hero.image != self.oryg_image:
                old_image = old_hero.image

            if old_hero.title != self.title:
                old_name = old_hero.title

        if (
            is_new_instance
            or old_name != self.title
            or old_image != self.oryg_image
        ):
            if is_new_instance or old_name != self.title:
                self.slug = slugify(
                    self.title.replace("ł", "l")
                    .replace("Ł", "L")
                    .replace("ą", "a")
                    .replace("ę", "e")
                    .replace("ś", "s")
                    .replace("ć", "c")
                    .replace("ń", "n")
                )

            if is_new_instance or old_image != self.oryg_image:
                if is_new_instance:
                    super().save(*args, **kwargs)
                if self.oryg_image:
                    self.thumbnails = generate_thumbnails(
                        self, False, self.order, "hero", self.oryg_image
                    )

        super().save(*args, **kwargs)

    @property
    def image(self):
        return self.hero_thumbnails.filter(
            width_expected=650, height_expected=650
        ).last()


@receiver(models.signals.pre_save, sender=Hero)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Hero.objects.get(pk=instance.pk).oryg_image
        new_file = instance.oryg_image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Hero.DoesNotExist:
        return False

    except Hero.DoesNotExist:
        return False


@receiver(models.signals.post_delete, sender=Hero)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.oryg_image:
        if os.path.isfile(instance.oryg_image.path):
            os.remove(instance.oryg_image.path)
