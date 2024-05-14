from datetime import timezone

from django.db import models
from django.db.models import Min
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField("Nazwa", max_length=255)
    slug = models.SlugField(
        "Slug", max_length=255, unique=True, blank=True, null=True
    )
    description = models.TextField("Opis", blank=True, null=True)

    class Meta:
        verbose_name = "Produkt"
        verbose_name_plural = "Produkty"
        ordering = ["name"]

    def save(self):
        self.slug = slugify(self.name.replace("ł", "l").replace("Ł", "L"))
        return super().save()

    def __str__(self):
        return self.name

    @property
    def current_price(self):
        current, _ = self.current_and_min_price()
        return current

    @property
    def min_price_last_30(self):
        _, min_last_30 = self.current_and_min_price()
        return min_last_30

    def current_and_min_price(self):
        current_price_obj = self.productprice_set.latest("created_date")
        current_price = current_price_obj.price

        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        if current_price_obj.created_date < thirty_days_ago:
            return current_price, current_price

        min_price = (
            self.productprice_set.exclude(pk=current_price_obj.pk)
            .filter(created_date__gte=thirty_days_ago)
            .aggregate(min_price=Min("price"))["min_price"]
        )
        if min_price is None:
            return current_price, current_price

        return current_price, min_price
