import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

from web.constants import ORDER_STATUS, PAYMENT_METHOD
from web.orders.functions import generate_order_number


class Order(models.Model):
    id = models.AutoField(primary_key=True) 
    uid = models.UUIDField(
        verbose_name="Unikalny identyfikator",
        db_index=True,
        default=uuid.uuid4, 
        editable=False,
        unique=True,  
    )
    created_date = models.DateTimeField(
        verbose_name="Data utworzenia zamówienia",
        default=timezone.now,
        db_index=True,
    )
    updated_date = models.DateTimeField(
        verbose_name="Data aktualizacji", auto_now=True
    )
    order_number = models.CharField(
        verbose_name="Numer zamówienia", max_length=255
    )
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
    client_mobile = models.CharField(
        verbose_name="Telefon klienta", max_length=15
    )

    amount = models.DecimalField(
        max_digits=10, verbose_name="Cena", decimal_places=2
    )
    amount_with_discount = models.DecimalField(
        max_digits=10,
        verbose_name="Cena z rabatem",
        decimal_places=2,
        blank=True,
        null=True,
    )
    discount = models.DecimalField(
        max_digits=10, verbose_name="Rabat", decimal_places=2, default=0
    )
    info = models.TextField(
        verbose_name="Informacje do zamówienia", null=True, blank=True
    )
    delivery_method = models.ForeignKey(
        "Delivery",
        on_delete=models.CASCADE,
        verbose_name="Sposób dostawy",
        related_name="orders",
    )
    # Payment
    payment_method = models.ForeignKey(
        "Payment",
        on_delete=models.CASCADE,
        verbose_name="Sposób płatności",
        related_name="orders",
    )
    payment_price = models.DecimalField(
        max_digits=10,
        verbose_name="Opłata za płatność",
        decimal_places=2,
        default=0,
    )
    payment_date = models.DateTimeField(
        verbose_name="Data płatności",
        null=True,
        blank=True,
    )
    checkout_session_id = models.CharField(
        verbose_name="Identyfikator płatności",
        max_length=255,
        null=True,
        blank=True,
    )
    is_paid = models.BooleanField(verbose_name="Opłacone", default=False)

    # Delivery
    delivery_method = models.ForeignKey(
        "Delivery",
        on_delete=models.CASCADE,
        verbose_name="Sposób dostawy",
        related_name="orders",
    )
    delivery_price = models.DecimalField(
        max_digits=10,
        verbose_name="Opłata za dostwę",
        decimal_places=2,
        default=0,
    )
    inpost_box_id = models.CharField(
        verbose_name="Id paczkomatu", max_length=255, null=True, blank=True
    )
    street = models.CharField(
        verbose_name="Ulica", max_length=255, null=True, blank=True
    )
    house_number = models.CharField(
        verbose_name="Numer domu", max_length=255, null=True, blank=True
    )
    local_number = models.CharField(
        verbose_name="Numer lokalu", max_length=255, null=True, blank=True
    )
    city = models.CharField(
        verbose_name="Miasto", max_length=255, null=True, blank=True
    )
    postal_code = models.CharField(
        verbose_name="Kod pocztowy", max_length=255, null=True, blank=True
    )

    # Items
    cart_items = models.JSONField(verbose_name="Produkty w koszyku", null=True)
    cart_items_price = models.DecimalField(
        max_digits=10,
        verbose_name="Cena produktów",
        decimal_places=2,
        default=0,
    )

    # Invoice
    make_invoice = models.BooleanField(
        verbose_name="Generuj fakturę?", default=False
    )
    invoice_created = models.BooleanField(
        verbose_name="Faktura utworzona", default=False
    )
    company = models.CharField(
        verbose_name="Nazwa firmy", max_length=255, null=True, blank=True
    )
    company_payer = models.TextField(
        verbose_name="Płatnik", null=True, blank=True
    )
    invoice_street = models.CharField(
        verbose_name="Ulica", max_length=255, null=True, blank=True
    )
    nip = models.CharField(
        verbose_name="NIP", max_length=255, null=True, blank=True
    )
    invoice_house_number = models.CharField(
        verbose_name="Numer domu", max_length=255, null=True, blank=True
    )
    invoice_local_number = models.CharField(
        verbose_name="Numer lokalu", max_length=255, null=True, blank=True
    )
    invoice_city = models.CharField(
        verbose_name="Miasto", max_length=255, null=True, blank=True
    )
    invoice_postal_code = models.CharField(
        verbose_name="Kod pocztowy", max_length=255, null=True, blank=True
    )

    email_notification = models.BooleanField(
        verbose_name="Czy wysyłac email", default=True
    )

    overriden_invoice_number = models.CharField(
        verbose_name="Nadpisz numer faktury",
        max_length=255,
        null=True,
        blank=True,
    )
    overriden_invoice_date = models.DateField(
        verbose_name="Nadpisz datę faktury", null=True, blank=True
    )
    link = models.URLField(
        verbose_name="Link do zamówienia", null=True, blank=True
    )

    class Meta:
        verbose_name = "Zamówienie"
        verbose_name_plural = "Zamówienia"
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.order_number} - {self.amount} zł"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        if not self.link:
            self.link = settings.SITE_URL + "koszyk/zamowienie-szczegoly?order_uid="  + str(self.uid)
        super().save(*args, **kwargs)


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
    name = models.CharField(
        verbose_name="Nazwa", max_length=255, db_index=True
    )
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
            return (
                self.name
                + f" {self.qty} x {self.price} zł ({self.discount}% rabatu)"
            )
        return self.name + f" {self.qty} x {self.price} zł"


class Invoice(models.Model):
    created_time = models.DateTimeField(
        verbose_name="Data utworzenia", default=timezone.now, db_index=True
    )
    order = models.OneToOneField(
        "Order", on_delete=models.CASCADE, null=True, blank=True, db_index=True, related_name="invoice"
    )
    number = models.CharField(max_length=64)
    override_number = models.CharField(
        verbose_name="Nadpisany numer faktury",
        max_length=64,
        null=True,
        blank=True,
    )
    override_date = models.DateField(
        verbose_name="Nadpisana data faktury", null=True, blank=True
    )
    pdf = models.FileField(null=True, blank=True)

    class Meta:
        ordering = ("-created_time",)
        verbose_name_plural = "Faktury"

    def __str__(self):
        return str(self.pdf)

    @property
    def full_path(self, request):
        return request.build_absolute_uri(settings.MEDIA_URL + self.pdf.url)
