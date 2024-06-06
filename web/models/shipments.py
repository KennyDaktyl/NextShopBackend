from django.db import models


class Shipment(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa")
    price = models.DecimalField(
        max_digits=10, verbose_name="Cena", decimal_places=2
    )
    is_active = models.BooleanField(verbose_name="Czy aktywna", default=True)

    class Meta:
        verbose_name = "Rodzaj dostawy"
        verbose_name_plural = "Rodzaj dostawy"
        ordering = ["name"]

    def __str__(self):
        return self.name + f" - {self.price} zł"
