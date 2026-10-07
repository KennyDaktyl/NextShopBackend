import os
import uuid
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from web.constants import ORDER_STATUS
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
    prev_status = models.IntegerField(
        "Poprzedni status", choices=ORDER_STATUS, default=0
    )
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
        max_digits=10,
        verbose_name="Rabat (%)",
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
        help_text=(
            "Rabat procentowy naliczany od ceny regularnej na wszystkie "
            "produkty w zamówieniu (bez dostawy i opłaty za płatność)."
        ),
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
        verbose_name="Numer domu na FV", max_length=255, null=True, blank=True
    )
    invoice_local_number = models.CharField(
        verbose_name="Numer lokalu na FV",
        max_length=255,
        null=True,
        blank=True,
    )
    invoice_city = models.CharField(
        verbose_name="Miasto na FV", max_length=255, null=True, blank=True
    )
    invoice_postal_code = models.CharField(
        verbose_name="Kod pocztowy na FV",
        max_length=255,
        null=True,
        blank=True,
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
    tracking_number = models.CharField(
        verbose_name="Numer przesyłki InPost",
        max_length=64,
        null=True,
        blank=True,
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
            self.link = (
                os.environ.get("NEXTJS_BASE_URL")
                + "koszyk/zamowienie-szczegoly?order_uid="
                + str(self.uid)
            )
        self.is_paid_changed = False
        self.is_status_changed = False
        self.is_discount_changed = False
        self.is_totals_changed = False
        if self.pk:
            old_order_data = Order.objects.get(pk=self.pk)
            if old_order_data.status != self.status:
                self.prev_status = old_order_data.status
                self.is_status_changed = True
            if old_order_data.is_paid != self.is_paid:
                self.is_paid_changed = True
            if old_order_data.discount != self.discount:
                self.is_discount_changed = True
            # Sumy liczymy przed zapisem, żeby sygnał post_save (faktura)
            # widział już kwoty po rabacie.
            if kwargs.get("update_fields") is None:
                if self.is_discount_changed:
                    self.apply_discount_to_items()
                self.recalculate_totals()
                self.is_totals_changed = self.totals != old_order_data.totals
        super().save(*args, **kwargs)

    def apply_discount_to_items(self):
        """Ustawia rabat zamówienia na wszystkich pozycjach-produktach."""
        self.order_items.filter(item_type=OrderItem.TYPE_PRODUCT).update(
            discount=self.discount
        )

    def recalculate_totals(self):
        """Przelicza kwoty zamówienia na podstawie pozycji.

        Zamówienia bez pozycji zostawiamy bez zmian. Zwraca True, jeśli
        kwoty zostały przeliczone.
        """
        items = list(self.order_items.all())
        if not items:
            return False

        def total(item_type):
            return sum(
                (
                    item.value_gross_after_discount
                    for item in items
                    if item.item_type == item_type
                ),
                Decimal("0.00"),
            )

        self.cart_items_price = total(OrderItem.TYPE_PRODUCT)
        self.delivery_price = total(OrderItem.TYPE_DELIVERY)
        self.payment_price = total(OrderItem.TYPE_PAYMENT)
        self.amount = sum(
            (item.value_gross_after_discount for item in items),
            Decimal("0.00"),
        )
        has_discount = any(item.discount for item in items)
        self.amount_with_discount = self.amount if has_discount else None
        return True

    def update_totals(self):
        """Przelicza i zapisuje kwoty bez wywoływania sygnałów Order."""
        if self.recalculate_totals():
            Order.objects.filter(pk=self.pk).update(
                amount=self.amount,
                amount_with_discount=self.amount_with_discount,
                cart_items_price=self.cart_items_price,
                delivery_price=self.delivery_price,
                payment_price=self.payment_price,
            )

    @property
    def totals(self):
        return (
            self.amount,
            self.cart_items_price,
            self.delivery_price,
            self.payment_price,
        )

    @property
    def has_discount(self):
        return any(item.discount for item in self.order_items.all())

    @property
    def regular_amount(self):
        """Suma brutto wszystkich pozycji przed rabatem."""
        return sum(
            (item.value_gross for item in self.order_items.all()),
            Decimal("0.00"),
        )

    @property
    def discount_amount(self):
        return self.regular_amount - self.amount

    @property
    def vat_summary(self):
        """Zestawienie według stawek VAT, liczone od sumy brutto w stawce.

        Metoda "od brutto" (art. 106e ust. 8): VAT = brutto * s / (100 + s)
        od sumy wartości sprzedaży w danej stawce, a nie suma VAT pozycji.
        """
        gross_by_rate = {}
        for item in self.order_items.all():
            gross_by_rate[item.vat_rate] = (
                gross_by_rate.get(item.vat_rate, Decimal("0.00"))
                + item.value_gross_after_discount
            )
        summary = []
        for rate, gross in sorted(gross_by_rate.items(), reverse=True):
            vat = round_money(gross * rate / (100 + rate))
            summary.append(
                {"rate": rate, "net": gross - vat, "vat": vat, "gross": gross}
            )
        return summary

    @property
    def net_amount(self):
        return sum((row["net"] for row in self.vat_summary), Decimal("0.00"))

    @property
    def vat_amount(self):
        return sum((row["vat"] for row in self.vat_summary), Decimal("0.00"))


def round_money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class OrderItem(models.Model):
    TYPE_PRODUCT = 0
    TYPE_DELIVERY = 1
    TYPE_PAYMENT = 2
    ITEM_TYPES = (
        (TYPE_PRODUCT, "Produkt"),
        (TYPE_DELIVERY, "Dostawa"),
        (TYPE_PAYMENT, "Opłata za płatność"),
    )

    order = models.ForeignKey(
        "Order",
        verbose_name="Zamówienie",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="order_items",
    )
    item_type = models.IntegerField(
        verbose_name="Rodzaj pozycji",
        choices=ITEM_TYPES,
        default=TYPE_PRODUCT,
    )
    product = models.ForeignKey(
        "Product",
        verbose_name="Produkt",
        on_delete=models.SET_NULL,
        db_index=True,
        related_name="items",
        null=True,
        blank=True,
    )
    name = models.CharField(
        verbose_name="Nazwa", max_length=255, db_index=True
    )
    variant = models.CharField(
        verbose_name="Wariant", max_length=255, null=True, blank=True
    )
    selected_option = models.CharField(
        verbose_name="Opcja", max_length=255, null=True, blank=True
    )
    qty = models.IntegerField(verbose_name="Ilość", default=1)
    price_net = models.DecimalField(
        max_digits=10,
        verbose_name="Cena netto",
        decimal_places=2,
        default=0,
        help_text="Liczona automatycznie z ceny brutto. Zmień tylko cenę "
        "netto, aby przeliczyć cenę brutto.",
    )
    price_gross = models.DecimalField(
        max_digits=10, verbose_name="Cena brutto", decimal_places=2, default=0
    )
    vat_rate = models.IntegerField(verbose_name="Stawka VAT (%)", default=23)
    discount = models.DecimalField(
        max_digits=5,
        verbose_name="Rabat (%)",
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(Decimal("0")),
            MaxValueValidator(Decimal("100")),
        ],
    )
    info = models.TextField(verbose_name="Komentarz", null=True, blank=True)

    class Meta:
        verbose_name = "Pozycja zamówienia"
        verbose_name_plural = "Pozycje zamówienia"
        ordering = ["item_type", "id"]

    def __str__(self):
        if self.discount:
            return (
                self.name
                + f" {self.qty} x {self.price_gross} zł"
                + f" ({self.discount}% rabatu)"
            )
        return self.name + f" {self.qty} x {self.price_gross} zł"

    def save(self, *args, **kwargs):
        # Źródłem prawdy jest cena brutto (Product.price to cena brutto).
        # Cenę brutto liczymy z netto tylko wtedy, gdy ręcznie zmieniono
        # wyłącznie cenę netto.
        old = None
        if self.pk:
            old = (
                OrderItem.objects.filter(pk=self.pk)
                .values("price_net", "price_gross", "vat_rate")
                .first()
            )
        if old is None:
            net_edited = not self.price_gross and self.price_net
        else:
            net_edited = (
                old["price_net"] != self.price_net
                and old["price_gross"] == self.price_gross
                and old["vat_rate"] == self.vat_rate
            )
        if net_edited:
            self.price_gross = round_money(
                Decimal(self.price_net) * self.vat_multiplier
            )
        else:
            self.price_net = self.net_from_gross(self.price_gross)
        super().save(*args, **kwargs)

    @property
    def vat_multiplier(self):
        return 1 + Decimal(self.vat_rate) / 100

    def net_from_gross(self, gross):
        return round_money(Decimal(gross) / self.vat_multiplier)

    @property
    def price_gross_after_discount(self):
        return round_money(
            Decimal(self.price_gross) * (100 - Decimal(self.discount)) / 100
        )

    @property
    def price_net_after_discount(self):
        return self.net_from_gross(self.price_gross_after_discount)

    @property
    def value_gross(self):
        return round_money(Decimal(self.price_gross) * self.qty)

    @property
    def value_net(self):
        return self.net_from_gross(self.value_gross)

    @property
    def value_gross_after_discount(self):
        return round_money(self.price_gross_after_discount * self.qty)

    @property
    def value_net_after_discount(self):
        return self.net_from_gross(self.value_gross_after_discount)

    @property
    def vat_value(self):
        return self.value_gross_after_discount - self.value_net_after_discount


class Invoice(models.Model):
    created_time = models.DateTimeField(
        verbose_name="Data utworzenia", default=timezone.now, db_index=True
    )
    order = models.OneToOneField(
        "Order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name="invoice",
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
