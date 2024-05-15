from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    order = models.IntegerField(verbose_name="Kolejność", default=1)
    name = models.CharField(max_length=100, verbose_name="Nazwa kategorii")
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
    is_main = models.BooleanField(
        verbose_name="Czy w menu głównym", default=False
    )
    is_active = models.BooleanField(verbose_name="Czy aktywna", default=True)

    def save(self, *args, **kwargs):
        if (
            not self.slug
            or self.name != self._meta.model.objects.get(pk=self.pk).name
        ):
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("order", "name")
        verbose_name_plural = "Kategorie"

    def get_full_path(self):
        path = [self.name]
        current_category = self.parent

        while current_category:
            path.insert(0, current_category.name)
            current_category = current_category.parent

        return " / ".join(path)

    @property
    def get_products(self):
        return self.products.filter(is_active=True)

    @property
    def get_products_count(self):
        return self.products.filter(is_active=True).count()
