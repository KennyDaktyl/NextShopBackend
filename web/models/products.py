from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Min
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from web.models.categories import Category
from web.models.prices import ProductPrice


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Kategoria",
        db_index=True,
        related_name="products",
    )
    name = models.CharField(
        verbose_name="Nazwa", max_length=255, db_index=True
    )
    slug = models.SlugField(
        "Slug", max_length=255, unique=True, blank=True, null=True
    )
    qty = models.IntegerField(verbose_name="Ilość", default=0)
    description = models.TextField(
        verbose_name="Opis produktu", blank=True, null=True
    )
    image = models.ImageField("verobse_name", upload_to="products", blank=True)
    is_active = models.BooleanField(verbose_name="Czy aktywny", default=True)

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"
        ordering = ["name"]

    def save(self):
        self.slug = slugify(self.name.replace("ł", "l").replace("Ł", "L"))
        return super().save()

    def __str__(self):
        return self.name

    def get_full_image_url(self, request):
        if self.image:
            return request.build_absolute_uri(
                settings.MEDIA_URL + self.image.url
            )
        return ""

    @property
    def current_price(self):
        try:
            latest_price = self.prices.latest("created_date")
            return latest_price.price
        except ProductPrice.DoesNotExist:
            return None

    @property
    def min_price_last_30(self):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        current_price = self.current_price
        min_price_query = (
            self.prices.filter(created_date__gte=thirty_days_ago)
            .exclude(price=current_price)
            .aggregate(min_price=Min("price"))["min_price"]
        )
        return (
            min_price_query if min_price_query is not None else current_price
        )

    def get_absolute_url(self):
        category_path = self.category.get_full_path()
        return f"{category_path}/{self.slug}"
    