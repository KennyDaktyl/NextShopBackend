import json
from decimal import ROUND_HALF_UP, Decimal

from django.db import migrations

TYPE_PRODUCT = 0
TYPE_DELIVERY = 1
TYPE_PAYMENT = 2
VAT_MULTIPLIER = Decimal("1.23")


def round_money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def to_decimal(value):
    try:
        return round_money(Decimal(str(value)))
    except Exception:
        return Decimal("0.00")


def cart_items_to_order_items(apps, schema_editor):
    """Przenosi produkty z JSON-a cart_items do pozycji OrderItem.

    Kwot zamówień nie zmieniamy - pozycje odtwarzają dokładnie to, co było
    na fakturze (produkty, usługa kurierska, opłata za płatność).
    Rabat z Order.discount trafia na pozycje-produkty; kwoty takich zamówień
    przeliczą się przy najbliższym zapisie w adminie.
    """
    Order = apps.get_model("web", "Order")
    OrderItem = apps.get_model("web", "OrderItem")
    Product = apps.get_model("web", "Product")

    product_ids = set(Product.objects.values_list("id", flat=True))
    orders_with_discount = []

    for order in Order.objects.select_related("delivery_method").iterator():
        if OrderItem.objects.filter(order=order).exists():
            continue

        cart_items = order.cart_items
        if isinstance(cart_items, str):
            try:
                cart_items = json.loads(cart_items)
            except ValueError:
                cart_items = []
        if not isinstance(cart_items, list):
            cart_items = []

        discount = order.discount or Decimal("0")
        if discount:
            orders_with_discount.append(f"{order.order_number} ({discount})")

        items = []
        for el in cart_items:
            if not isinstance(el, dict):
                continue
            gross = to_decimal(el.get("price", 0))
            product_id = el.get("id")
            items.append(
                OrderItem(
                    order=order,
                    item_type=TYPE_PRODUCT,
                    product_id=product_id if product_id in product_ids else None,
                    name=(el.get("name") or "Produkt")[:255],
                    variant=el.get("variant"),
                    selected_option=el.get("selected_option"),
                    info=el.get("info"),
                    qty=int(el.get("quantity") or 1),
                    price_gross=gross,
                    price_net=round_money(gross / VAT_MULTIPLIER),
                    discount=discount,
                )
            )

        delivery_price = order.delivery_price or Decimal("0")
        if not order.delivery_method.in_store_pickup or delivery_price:
            items.append(
                OrderItem(
                    order=order,
                    item_type=TYPE_DELIVERY,
                    name="Usługa kurierska",
                    price_gross=delivery_price,
                    price_net=round_money(delivery_price / VAT_MULTIPLIER),
                )
            )

        payment_price = order.payment_price or Decimal("0")
        if payment_price:
            items.append(
                OrderItem(
                    order=order,
                    item_type=TYPE_PAYMENT,
                    name="Płatność za pobraniem",
                    price_gross=payment_price,
                    price_net=round_money(payment_price / VAT_MULTIPLIER),
                )
            )

        OrderItem.objects.bulk_create(items)

    if orders_with_discount:
        print(
            "\n  Zamówienia z rabatem - zapisz je w adminie, aby przeliczyć "
            "kwoty i fakturę: " + ", ".join(orders_with_discount)
        )


def delete_order_items(apps, schema_editor):
    apps.get_model("web", "OrderItem").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0131_order_items_discount"),
    ]

    operations = [
        migrations.RunPython(cart_items_to_order_items, delete_order_items),
    ]
