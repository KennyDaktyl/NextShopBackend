from django.db import models
from django.utils import timezone


class ProductPrice(models.Model):
    product = models.ForeignKey(
        "Product",
        verbose_name="Produkt",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="prices",
    )
    price = models.DecimalField(
        max_digits=10, verbose_name="Cena", decimal_places=2
    )
    created_date = models.DateTimeField(
        verbose_name="Data utworzenia ceny",
        default=timezone.now,
        db_index=True,
    )
    expired_date = models.DateTimeField(
        verbose_name="Data wygaśnięcia ceny",
        blank=True,
        null=True,
        db_index=True,
    )
    
    class Meta:
        verbose_name = "Cena produktu"
        verbose_name_plural = "Ceny produktów"
        ordering = ["-product__name", "-created_date"]

    def save(self, *args, **kwargs):
        if not self.pk:  
            last_price = ProductPrice.objects.filter(
                product=self.product, expired_date__isnull=True
            ).order_by('-created_date').first()

            if last_price:
                last_price.expired_date = timezone.now()
                last_price.save()

        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.price} zł"


class PriceGroup(models.Model):
    name = models.CharField(verbose_name="Grupa cenowa", max_length=100)
    discount_rate = models.IntegerField(
        verbose_name="Przyznany rabat w %", default=0
    )

    class Meta:
        verbose_name = "Grupa cenowa"
        verbose_name_plural = "Grupy cenowe"
        ordering = ["name"]

    def __str__(self):
        return self.name + f" - {self.discount_rate}%"
