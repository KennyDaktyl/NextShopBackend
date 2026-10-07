from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0130_order_tracking_number"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="orderitem",
            options={
                "ordering": ["item_type", "id"],
                "verbose_name": "Pozycja zamówienia",
                "verbose_name_plural": "Pozycje zamówienia",
            },
        ),
        migrations.RenameField(
            model_name="orderitem",
            old_name="price",
            new_name="price_gross",
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="price_gross",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name="Cena brutto",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="price_net",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Liczona automatycznie z ceny brutto. Zmień tylko cenę netto, aby przeliczyć cenę brutto.",
                max_digits=10,
                verbose_name="Cena netto",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="item_type",
            field=models.IntegerField(
                choices=[
                    (0, "Produkt"),
                    (1, "Dostawa"),
                    (2, "Opłata za płatność"),
                ],
                default=0,
                verbose_name="Rodzaj pozycji",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="variant",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Wariant"
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="selected_option",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="Opcja"
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="vat_rate",
            field=models.IntegerField(
                default=23, verbose_name="Stawka VAT (%)"
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0")),
                    django.core.validators.MaxValueValidator(Decimal("100")),
                ],
                verbose_name="Rabat (%)",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="order_items",
                to="web.order",
                verbose_name="Zamówienie",
            ),
        ),
        migrations.AlterField(
            model_name="orderitem",
            name="product",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="items",
                to="web.product",
                verbose_name="Produkt",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="discount",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Rabat procentowy naliczany od ceny regularnej na wszystkie produkty w zamówieniu (bez dostawy i opłaty za płatność).",
                max_digits=10,
                validators=[
                    django.core.validators.MinValueValidator(Decimal("0")),
                    django.core.validators.MaxValueValidator(Decimal("100")),
                ],
                verbose_name="Rabat (%)",
            ),
        ),
    ]
