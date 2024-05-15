from django.utils import timezone

from django.db import models
from django.utils.text import slugify

from web.constants import PAYMENT_METHOD, ORDER_STATUS


class Order(models.Model):
    created_date = models.DateTimeField(
        verbose_name="Data utworzenia zamówienia",
        default=timezone.now,
        db_index=True,
    )
    updated_date = models.DateTimeField(verbose_name="Data aktualizacji", auto_now=True)
    order_number = models.CharField(verbose_name="Numer zamówienia", max_length=255)
    status = models.IntegerField("Status", choices=ORDER_STATUS, default=0)
    client = models.ForeignKey(
        "auth.User",
        verbose_name="Klient",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="orders",
        null=True,
        blank=True,
    )
    client_name = models.CharField(
        verbose_name="Imię i nazwisko klienta", max_length=255
    )
    client_email = models.EmailField(
        verbose_name="Email klienta", max_length=255
    )
    client_phone = models.CharField(
        verbose_name="Telefon klienta", max_length=15
    )
    client_address = models.CharField(
        verbose_name="Adres klienta", max_length=255
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
    delivery_method = models.ForeignKey("Shipment", on_delete=models.CASCADE, verbose_name="Sposób dostawy")
    # Payment
    payment_method = models.IntegerField("Status", choices=PAYMENT_METHOD, default=0)
    payment_date = models.DateTimeField(
        verbose_name="Data płatności",
        null=True,
        blank=True,
    )
    payment_id = models.CharField(
        verbose_name="Identyfikator płatności",
        max_length=255,
        null=True,
        blank=True,
    )
    order_code = models.CharField(verbose_name="Kod płatności", max_length=255, null=True, blank=True)
    
    # Invoice
    invoice = models.BooleanField(verbose_name="Faktura", default=False)
    email_notification = models.BooleanField(verbose_name="Czy wysyłac email", default=True)

    overriden_invoice_number = models.CharField(verbose_name="Nadpisz numer faktury", max_length=255, null=True, blank=True)
    overriden_invoice_date = models.DateField(verbose_name="Nadpisz datę faktury", null=True, blank=True)

    class Meta:
        verbose_name = "Zamówienie"
        verbose_name_plural = "Zamówienia"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.product.name} - {self.price} zł"
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        "Order",
        verbose_name="Koszyk",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="order_items",
    )
    product = models.ForeignKey(
        "Product",
        verbose_name="Produkt",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="items",
    )
    name = models.CharField(verbose_name="Nazwa", max_length=255, db_index=True)
    qty = models.IntegerField(verbose_name="Ilość", default=1)
    price = models.DecimalField(
        max_digits=10, verbose_name="Cena", decimal_places=2
    )
    discount = models.IntegerField(verbose_name="Rabat", default=0)
    info = models.TextField(verbose_name="Komentarz", null=True, blank=True)

    class Meta:
        verbose_name = "Produkt w zamówieniu"
        verbose_name_plural = "Produkty w zamówieniu"
        ordering = ["name"]

    def __str__(self):
        if self.discount:
            return self.name + f" {self.qty} x {self.price} zł ({self.discount}% rabatu)"
        return self.name + f" {self.qty} x {self.price} zł"
    