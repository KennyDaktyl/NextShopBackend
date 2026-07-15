from decimal import Decimal

from django.db import migrations
from django.utils.text import slugify


def polish_slugify(name):
    return slugify(
        name.replace("ł", "l")
        .replace("Ł", "L")
        .replace("ą", "a")
        .replace("ę", "e")
        .replace("ś", "s")
        .replace("ć", "c")
        .replace("ń", "n")
        .replace("ó", "o")
        .replace("ż", "z")
        .replace("ź", "z")
        .replace("Ą", "A")
        .replace("Ę", "E")
        .replace("Ś", "S")
        .replace("Ć", "C")
        .replace("Ń", "N")
        .replace("Ó", "O")
        .replace("Ż", "Z")
        .replace("Ź", "Z")
        .replace(" ", "-")
        .replace("---", "-")
    )


KEY_TYPES = [
    (
        "Klucze mieszkaniowe",
        "Do drzwi wejściowych, piwnic, skrzynek pocztowych.",
        Decimal("15.00"),
    ),
    (
        "Klucze samochodowe",
        "Z immobilizerem, dorobione i skonfigurowane na miejscu.",
        Decimal("180.00"),
    ),
    (
        "Zdalniki i piloty",
        "Dorobienie i programowanie pilotów do samochodu.",
        Decimal("150.00"),
    ),
    (
        "Klucze zabezpieczone",
        "Klucze systemowe i atestowane, na zamówienie.",
        Decimal("35.00"),
    ),
]

STAMP_TYPES = [
    (
        "Pieczątki firmowe",
        "Nazwa, NIP, adres, logo — pod faktury i dokumenty.",
        Decimal("45.00"),
    ),
    (
        "Pieczątki imienne",
        "Dla lekarzy, prawników, księgowych.",
        Decimal("40.00"),
    ),
    (
        "Pieczątki samotuszujące",
        "Automatyczne, tysiące odbić bez poduszki.",
        Decimal("55.00"),
    ),
    (
        "Pieczątki z datownikiem",
        "Okrągłe firmowe i urzędowe.",
        Decimal("50.00"),
    ),
    (
        "Pieczątki drewniane",
        "Klasyczna oprawa z poduszką w komplecie.",
        Decimal("35.00"),
    ),
    (
        "Duplikaty i naprawy",
        "Zgubiona lub zniszczona pieczątka — duplikat tego samego dnia.",
        Decimal("40.00"),
    ),
]

CONTACT_PHONE = "506029980"
WHATSAPP_URL = "https://wa.me/48506029980"
MESSENGER_URL = "https://m.me/100032867754031"


def create_service_products(category, items):
    from web.models.products import Product
    from web.models.prices import ProductPrice

    products = [
        Product(
            category=category,
            name=name,
            description=desc,
            is_service=True,
            is_active=True,
        )
        for name, desc, _price in items
    ]
    created = Product.objects.bulk_create(products)

    for product in created:
        product.slug = f"{polish_slugify(product.name)}-id-{product.id}"
    Product.objects.bulk_update(created, ["slug"])

    ProductPrice.objects.bulk_create(
        [
            ProductPrice(product=product, price=price)
            for product, (_name, _desc, price) in zip(created, items)
        ]
    )


def seed_mobile_services(apps, schema_editor):
    from web.models.categories import Category, MobileServiceSettings

    uslugi = Category.objects.filter(slug="uslugi").first()
    if not uslugi:
        return

    (keys_category,) = Category.objects.bulk_create(
        [
            Category(
                parent=uslugi,
                name="Mobilne dorabianie kluczy",
                slug="mobilne-dorabianie-kluczy",
                item_label="Mobilne dorabianie kluczy",
                h1_tag="Dorabianie kluczy z dojazdem do klienta — Kraków i okolice",
                meta_title="Dorabianie kluczy z dojazdem do klienta — Kraków",
                meta_description=(
                    "Dorabianie kluczy mieszkaniowych i samochodowych z dojazdem "
                    "do klienta w Krakowie i okolicy. Dojazd do 2h od zamówienia."
                ),
                description="Dorabianie kluczy z dojazdem do klienta na terenie Krakowa i okolic.",
                seo_text=(
                    "Dorabiamy klucze mieszkaniowe i samochodowe z dojazdem do klienta na "
                    "terenie Krakowa i okolicznych miejscowości. Klucz dostarczamy do 2 godzin "
                    "od przyjęcia zamówienia — bez konieczności przyjazdu do punktu w Rybnej."
                ),
                order=0,
                is_active=True,
            )
        ]
    )
    create_service_products(keys_category, KEY_TYPES)
    MobileServiceSettings.objects.create(
        category=keys_category,
        min_keys_qty=3,
        wholesale_qty=10,
        wholesale_discount_percent=15,
        delivery_time_hours=2,
        phone_number=CONTACT_PHONE,
        whatsapp_url=WHATSAPP_URL,
        messenger_url=MESSENGER_URL,
    )

    (stamps_category,) = Category.objects.bulk_create(
        [
            Category(
                parent=uslugi,
                name="Mobilne wyrób pieczątek",
                slug="mobilne-wyrob-pieczatek",
                item_label="Mobilne pieczątki",
                h1_tag="Wyrób pieczątek ekspresowo z dojazdem do klienta",
                meta_title="Wyrób pieczątek ekspresowo z dojazdem do klienta — Kraków",
                meta_description=(
                    "Pieczątki firmowe, imienne i samotuszujące z dostawą do domu lub "
                    "biura w Krakowie i okolicy. Realizacja tego samego dnia, dojazd do 2h."
                ),
                description="Wyrób pieczątek z dojazdem do klienta na terenie Krakowa i okolic.",
                seo_text=(
                    "Wyrób pieczątek ekspresowo z dojazdem do klienta świadczymy na terenie "
                    "Krakowa i okolicznych miejscowości. Projekt akceptujesz zdalnie, a gotową "
                    "pieczątkę dostarczamy do 2 godzin — bez wizyty w punkcie w Rybnej."
                ),
                order=2,
                is_active=True,
            )
        ]
    )
    create_service_products(stamps_category, STAMP_TYPES)
    MobileServiceSettings.objects.create(
        category=stamps_category,
        min_stamp_order_value=Decimal("100.00"),
        wholesale_qty=10,
        wholesale_discount_percent=15,
        delivery_time_hours=2,
        phone_number=CONTACT_PHONE,
        whatsapp_url=WHATSAPP_URL,
        messenger_url=MESSENGER_URL,
    )


def remove_mobile_services(apps, schema_editor):
    from web.models.categories import Category

    Category.objects.filter(
        slug__in=["mobilne-dorabianie-kluczy", "mobilne-wyrob-pieczatek"]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0121_mobileservicesettings"),
    ]

    operations = [
        migrations.RunPython(seed_mobile_services, remove_mobile_services),
    ]
