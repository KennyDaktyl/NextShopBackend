from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify

from web.models.images import generate_thumbnails


class Article(models.Model):
    name = models.CharField(max_length=256, verbose_name="Tytuł")
    description = models.CharField(
        max_length=512, verbose_name="Opis", blank=True, null=True
    )
    slug = models.SlugField(
        max_length=256, verbose_name="Slug", blank=True, null=True
    )
    created_date = models.DateTimeField(
        verbose_name="Data utworzenia", auto_now_add=True
    )
    modified_date = models.DateTimeField(
        verbose_name="Data modyfikacji", auto_now=True
    )
    category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        verbose_name="Kategoria",
        related_name="articles",
    )
    prev_category = models.ForeignKey(
        "Category",
        on_delete=models.CASCADE,
        verbose_name="Poprzednia kategoria",
        related_name="prev_articles",
        blank=True,
        null=True,
    )
    oryg_image = models.ImageField(
        verbose_name="Zdjęcie",
        upload_to="articles",
        blank=True,
        null=True,
    )
    image_alt = models.CharField(
        verbose_name="Tekst alternatywny",
        max_length=255,
        blank=True,
        null=True,
    )
    image_title = models.CharField(
        verbose_name="Tytuł zdjęcia",
        max_length=255,
        blank=True,
        null=True,
    )
    content = models.TextField(verbose_name="Treść")
    meta_description = models.CharField(
        verbose_name="Meta description dla artykułu",
        blank=True,
        null=True,
        max_length=160,
    )
    meta_title = models.CharField(
        verbose_name="Meta title dla artykułu",
        blank=True,
        null=True,
        max_length=60,
    )
    thumbnails = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "Artykuł"
        verbose_name_plural = "Artykuły"
        ordering = ["-created_date"]

    def save(self, *args, **kwargs):
        is_new_instance = not self.pk
        old_image = None
        old_name = None

        if self.pk:
            if not self.oryg_image:
                self.thumbnails = {}
            old_article = Article.objects.get(pk=self.pk)
            old_name = old_article.name
            old_image = old_article.oryg_image

            if old_article.category != self.category:
                self.prev_category = old_article.category

            if (
                old_article.oryg_image
                and old_article.oryg_image != self.oryg_image
            ):
                old_image = old_article.oryg_image

            if old_article.name != self.name:
                old_name = old_article.name

            if self.oryg_image and old_image != self.oryg_image:
                thumbs = self.article_thumbnails.filter(main=True)
                if thumbs:
                    thumbs.delete()
        super().save(*args, **kwargs)

        if is_new_instance or old_name != self.name or self.slug is None:
            self.slug = f"{slugify(self.name .replace('ł', 'l').replace('Ł', 'L'))}-id-{self.id}"

        if is_new_instance or old_image != self.oryg_image and self.oryg_image:
            if self.oryg_image:
                self.thumbnails = generate_thumbnails(
                    self,
                    True,
                    False,
                    "article",
                    self.oryg_image,
                    alt=self.image_alt,
                    title=self.image_title,
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def image(self):
        return (
            self.article_thumbnails.filter(
                main=True, width_expected="350", height_expected="350"
            )
            .order_by("order")
            .first()
        )

    @property
    def image_listing(self):
        return (
            self.article_thumbnails.filter(
                main=True, width_expected="350", height_expected="350"
            )
            .order_by("order")
            .first()
        )

    @property
    def gallery(self):
        return self.article_thumbnails.filter(
            main=False,
            width_expected__in=["350", "650"],
            height_expected__in=["350", "650"],
        ).order_by("order")

    @property
    def full_path(self):
        return f"/blog/{self.slug}"
