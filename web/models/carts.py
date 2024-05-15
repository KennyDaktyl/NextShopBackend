from django.utils import timezone

from django.db import models


class Cart(models.Model):
    created_date = models.DateTimeField(
        verbose_name="Data utworzenia koszyka",
        default=timezone.now,
        db_index=True,
    )
    updated_date = models.DateTimeField(verbose_name="Data aktualizacji", auto_now=True)
    client = models.ForeignKey(
        "auth.User",
        verbose_name="Klient",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="carts",
    )
    amount = models.DecimalField(
        max_digits=10, verbose_name="Cena", decimal_places=2
    )
    amount_with_discount = models.DecimalField(
        max_digits=10, verbose_name="Cena z rabatem", decimal_places=2
    )
    discount = models.DecimalField(
        max_digits=10, verbose_name="Rabat", decimal_places=2
    )
    info = models.TextField(
        verbose_name="Komentarz", null=True, blank=True
    )

    class Meta:
        verbose_name = "Zapisany koszyk"
        verbose_name_plural = "Zapisane koszyki"
        ordering = ["-created_date"]

    def __str__(self):
        return f"Koszyk {self.client} - {self.created_date}"
    

class CartItem(models.Model):
    cart = models.ForeignKey(
        "Cart",
        verbose_name="Koszyk",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="items",
    )
    product = models.ForeignKey(
        "Product",
        verbose_name="Produkt",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="cart_items",
    )
    name = models.CharField(verbose_name="Nazwa", max_length=255, db_index=True)
    qty = models.IntegerField(verbose_name="Ilość", default=1)
    price = models.DecimalField(
        max_digits=10, verbose_name="Cena", decimal_places=2
    )
    discount = models.IntegerField(verbose_name="Rabat", default=0)
    info = models.TextField(verbose_name="Komentarz", null=True, blank=True)

    class Meta:
        verbose_name = "Produkt w koszyku"
        verbose_name_plural = "Produkty w koszyku"
        ordering = ["name"]

    def __str__(self):
        if self.discount:
            return self.name + f" {self.qty} x {self.price} zł ({self.discount}% rabatu)"
        return self.name + f" {self.qty} x {self.price} zł"
    