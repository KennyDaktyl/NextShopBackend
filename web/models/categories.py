import os

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify

from web.models.images import generate_thumbnails


class Category(models.Model):
    created_date = models.DateTimeField(
        verbose_name="Data utworzenia", auto_now_add=True
    )
    modified_date = models.DateTimeField(
        verbose_name="Data modyfikacji", auto_now=True
    )
    meta_title = models.CharField(
        max_length=60, verbose_name="Meta title", blank=True, null=True
    )
    meta_description = models.CharField(
        max_length=160, verbose_name="Meta description", blank=True, null=True
    )
    order = models.IntegerField(verbose_name="Kolejność", default=1)
    h1_tag = models.CharField(
        max_length=100, verbose_name="Nagłówek H1", blank=True, null=True
    )
    name = models.CharField(max_length=100, verbose_name="Nazwa kategorii")
    item_label = models.CharField(
        max_length=100, verbose_name="Etykieta w menu", blank=True, null=True
    )
    on_first_page = models.BooleanField(
        verbose_name="Czy widoczna na 1 stronie?", default=False
    )
    slug = models.SlugField(
        unique=True, max_length=255, verbose_name="Slug", null=True, blank=True
    )
    description = models.TextField(
        verbose_name="Opis kategorii", null=True, blank=True
    )
    seo_text = models.TextField(
        verbose_name="Tekst SEO", blank=True, null=True
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        verbose_name="Kategoria rodzic",
    )
    oryg_image = models.ImageField(
        verbose_name="Zdjęcie kategorii", upload_to="categories", blank=True
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
            # Pobieramy starą instancję kategorii
            old_category = Category.objects.get(pk=self.pk)
            old_name = old_category.name

            # Sprawdzamy czy obraz istnieje przed przypisaniem
            if old_category.oryg_image:
                old_image = old_category.oryg_image

            if old_category.name != self.name:
                old_name = old_category.name

        # Tworzenie slug na podstawie nowej nazwy
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

        # Ustawiamy etykietę, jeśli jest pusta
        if not self.item_label:
            self.item_label = self.name

        # Zapisujemy nową instancję kategorii
        super().save(*args, **kwargs)

        if not self.oryg_image or old_image != self.oryg_image:
            self.thumbnails = {}
            thumbs = self.category_thumbnails.filter(
                    main=True, order=1
                )
            if thumbs:
                thumbs.delete()
        # Generujemy miniaturki tylko po zapisaniu nowej kategorii lub zmianie obrazu
        if old_image != self.oryg_image and self.oryg_image:
            self.thumbnails = generate_thumbnails(
                self,
                True,
                False,
                "category",
                self.oryg_image,
                alt=self.image_alt,
                title=self.image_title,
            )

        # Ponowne zapisanie po wygenerowaniu miniaturek
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
    def products_count(self):
        return self.products.filter(is_active=True).count()

    @property
    def products_on_first_page(self):
        products = set(
            self.products.filter(is_active=True, on_first_page=True)
        )
        descendants = self.get_descendants()
        for descendant in descendants:
            products.update(
                descendant.products.filter(is_active=True, on_first_page=True)
            )
        return products

    @property
    def all_subcategories(self):
        subcategories = set()
        descendants = self.get_descendants()
        for descendant in descendants:
            subcategories.add(descendant)
        return subcategories

    def get_descendants(self):
        descendants = set()

        def _get_children(category):
            children = category.children.filter(is_active=True)
            for child in children:
                descendants.add(child)
                _get_children(child)

        _get_children(self)
        return descendants

    @property
    def has_parent(self):
        return True if self.parent else False

    @property
    def has_children(self):
        return self.children.filter(is_active=True).exists()

    def get_full_image_url(self, request):
        if self.oryg_image:
            return request.build_absolute_uri(
                settings.MEDIA_URL + self.oryg_image.url
            )
        return ""

    @property
    def image(self):
        return self.category_thumbnails.filter(
            width_expected=350, height_expected=350, main=True
        ).first()

    @property
    def full_path(self):
        return f"/produkty/{self.slug}"


@receiver(models.signals.pre_save, sender=Category)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_file = Category.objects.get(pk=instance.pk).oryg_image
        new_file = instance.oryg_image
        if old_file and not old_file == new_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)
    except Category.DoesNotExist:
        return False

    except Category.DoesNotExist:
        return False


@receiver(models.signals.post_delete, sender=Category)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.oryg_image:
        if os.path.isfile(instance.oryg_image.path):
            os.remove(instance.oryg_image.path)
