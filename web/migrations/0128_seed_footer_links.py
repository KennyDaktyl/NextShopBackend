from django.db import migrations

LINKS = [
    (
        "dowieziemycie.pl",
        "https://dowieziemycie.pl",
        "Przejdź do dowieziemycie.pl — lokalny transport osób w okolicy Krakowa",
        "partner",
        10,
    ),
    (
        "transfer247.pl",
        "https://transfer247.pl",
        "Przejdź do transfer247.pl — transfery lotniskowe i wycieczki w Małopolsce",
        "partner",
        20,
    ),
    (
        "smart-controller.tech",
        "https://smart-controller.tech",
        "Przejdź do smart-controller.tech — portfolio programisty, twórcy tego serwisu",
        "author",
        30,
    ),
]


def seed(apps, schema_editor):
    FooterLink = apps.get_model("web", "FooterLink")
    for name, url, description, link_type, order in LINKS:
        FooterLink.objects.get_or_create(
            url=url,
            defaults={
                "name": name,
                "description": description,
                "link_type": link_type,
                "order": order,
            },
        )


def unseed(apps, schema_editor):
    FooterLink = apps.get_model("web", "FooterLink")
    FooterLink.objects.filter(url__in=[link[1] for link in LINKS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0127_footerlink"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
