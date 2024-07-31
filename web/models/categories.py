import os

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify

from web.models.images import generate_thumbnails


class Category(models.Model):
    order = models.IntegerField(verbose_name="Kolejność", default=1)
    name = models.CharField(max_length=100, verbose_name="Nazwa kategorii")
    main = models.BooleanField(
        verbose_name="Czy kategoria główna", default=False
    )
    slug = models.SlugField(
        unique=True, max_length=255, verbose_name="Slug", null=True, blank=True
    )
    description = models.TextField(
        verbose_name="Opis kategorii", null=True, blank=True
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name="Kategoria rodzic",
    )
    image = models.ImageField(
        verbose_name="Zdjęcie kategorii", upload_to="categories", blank=True
    )
    is_main = models.BooleanField(
        verbose_name="Czy w menu głównym", default=False
    )
    is_active = models.BooleanField(verbose_name="Czy aktywna", default=True)
    thumbnails = models.JSONField(default=dict, blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None

        if self.pk:
            if not self.image:
                self.thumbnails = {}
            old_category = Category.objects.get(pk=self.pk)
            old_name = old_category.name
            old_image = old_category.image

            if old_category.image and old_category.image != self.image:
                old_image = old_category.image

            if old_category.name != self.name:
                old_name = old_category.name

        if is_new_instance or old_name != self.name:
            self.slug = slugify(
                self.name.replace("ł", "l")
                .replace("Ł", "L")
                .replace("ą", "a")
                .replace("ę", "e")
                .replace("ś", "s")
                .replace("ć", "c")
                .replace("ń", "n")
                .replace("ó", "o")
                .replace("ż", "z")
                .replace("ź", "z")
                .replace("Ą", "A")
                .replace("Ę", "E")
                .replace("Ś", "S")
                .replace("Ć", "C")
                .replace("Ń", "N")
                .replace("Ó", "O")
                .replace("Ż", "Z")
                .replace("Ź", "Z")
                .replace(" ", "-")
                .replace("---", "-")
            )

        if old_image and old_image != self.image:
            thumbs = self.category_thumbnails.filter(main=True)
            if thumbs:
                thumbs.delete()

        if is_new_instance or old_image != self.image and self.image:
            self.thumbnails = generate_thumbnails(
                self, True, False, "category", self.image
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("order", "name")
        verbose_name_plural = "Kategorie"

    def get_full_path(self):
        path = [self.slug]
        current_category = self.parent

        while current_category:
            path.insert(0, current_category.slug)
            current_category = current_category.parent

        return "/" + "/".join(path) if path else "/"

    def get_back_link(self):
        path = []
        current_category = self.parent

        while current_category:
            path.insert(0, current_category.slug)
            current_category = current_category.parent

        return "/" + "/".join(path) if path else "/"

    @property
    def get_products(self):
        return self.products.filter(is_active=True)

    @property
    def get_products_count(self):
        return self.products.filter(is_active=True).count()

    @property
    def has_parent(self):
        return True if self.parent else False

    @property
    def has_children(self):
        return self.children.filter(is_active=True).exists()

    def get_full_image_url(self, request):
        if self.image:
            return request.build_absolute_uri(
                settings.MEDIA_URL + self.image.url
            )
        return ""

    @property
    def image_list_item(self):
        return self.category_thumbnails.filter(
            width_expected=350, height_expected=350, main=True
        ).first()

    def get_descendants(self):
        descendants = set()

        def _get_children(category):
            children = category.children.filter(is_active=True)
            for child in children:
                descendants.add(child)
                _get_children(child)

        _get_children(self)
        return descendants

    def get_absolute_url(self):
        return f"/produkty/{self.slug}"


@receiver(models.signals.pre_save, sender=Category)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Category.objects.get(pk=instance.pk).image
        new_file = instance.image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Category.DoesNotExist:
        return False

    except Category.DoesNotExist:
        return False


@receiver(models.signals.post_delete, sender=Category)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
