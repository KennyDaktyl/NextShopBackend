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


LOCALITIES = [
    (
        "Krzeszowice",
        "Gmina Krzeszowice",
        "Krzeszowice leżą przy trasie z Krakowa do Katowic (DK79), znane są z zamku "
        "Potockich i term. To jedna z większych miejscowości powiatu krakowskiego na "
        "zachód od Rybnej.",
    ),
    (
        "Alwernia",
        "Gmina Alwernia",
        "Alwernia, znana z klasztoru Bernardynów i lokalnego przemysłu chemicznego, "
        "leży w powiecie chrzanowskim, na zachód od Krakowa.",
    ),
    (
        "Liszki",
        "Gmina Liszki",
        "Liszki to siedziba podkrakowskiej gminy rolniczej, położonej w dolinie Wisły, "
        "sąsiadującej bezpośrednio z Rybną.",
    ),
    (
        "Czernichów",
        "Gmina Czernichów",
        "Czernichów, siedziba gminy nad Wisłą, sąsiaduje z Liszkami i leży niedaleko "
        "Tyńca i Skawiny.",
    ),
    (
        "Balice",
        "Gmina Zabierzów",
        "Balice to miejscowość znana przede wszystkim z Portu Lotniczego Kraków-Balice "
        "im. Jana Pawła II, leżąca w gminie Zabierzów.",
    ),
    (
        "Rząska",
        "Gmina Zabierzów",
        "Rząska sąsiaduje z Balicami i lotniskiem, tuż przy granicy Krakowa od strony "
        "Bronowic.",
    ),
    (
        "Zabierzów",
        "Gmina Zabierzów",
        "Zabierzów, siedziba gminy przy linii kolejowej Kraków–Katowice, to jedna z "
        "większych podkrakowskich miejscowości na zachód od miasta.",
    ),
    (
        "Krowodrza",
        "Kraków — Krowodrza",
        "Krowodrza to dzielnica Krakowa z dużymi osiedlami mieszkaniowymi, blisko "
        "centrum miasta.",
    ),
    (
        "Łagiewniki",
        "Kraków — Łagiewniki-Borek Fałęcki",
        "Łagiewniki to dzielnica Krakowa znana z Sanktuarium Bożego Miłosierdzia, "
        "z przewagą zabudowy jednorodzinnej.",
    ),
    (
        "Borek Fałęcki",
        "Kraków — Łagiewniki-Borek Fałęcki",
        "Borek Fałęcki to dawna podkrakowska wieś, dziś część dzielnicy Łagiewniki-Borek "
        "Fałęcki, z przewagą domów jednorodzinnych.",
    ),
    (
        "Skawina",
        "Powiat krakowski",
        "Skawina, miasto nad Skawinką i Wisłą, leży na południowy zachód od Krakowa i "
        "jest jednym z większych ośrodków powiatu krakowskiego.",
    ),
    (
        "Podgórze",
        "Kraków — Podgórze",
        "Podgórze to prawobrzeżna, historyczna dzielnica Krakowa z własnym rynkiem, "
        "położona na przeciwko Starego Miasta.",
    ),
    (
        "Śródmieście",
        "Kraków — Śródmieście",
        "Śródmieście to historyczne centrum Krakowa ze Starym Miastem i Rynkiem "
        "Głównym.",
    ),
    (
        "Prądnik Czerwony",
        "Kraków — Prądnik Czerwony",
        "Prądnik Czerwony to dzielnica z dużymi osiedlami mieszkaniowymi na północ od "
        "centrum Krakowa.",
    ),
    (
        "Prądnik Biały",
        "Kraków — Prądnik Biały",
        "Prądnik Biały sąsiaduje z Krowodrzą i Prądnikiem Czerwonym, obejmuje m.in. "
        "osiedle Azory.",
    ),
    (
        "Azory",
        "Kraków — Prądnik Biały",
        "Azory to popularne osiedle mieszkaniowe w dzielnicy Prądnik Biały, blisko "
        "Parku Krakowskiego.",
    ),
    (
        "Wieliczka",
        "Powiat wielicki",
        "Wieliczka, znana na całym świecie z zabytkowej Kopalni Soli wpisanej na listę "
        "UNESCO, leży tuż na wschód od Krakowa.",
    ),
    (
        "Nowa Huta",
        "Kraków — Nowa Huta",
        "Nowa Huta to duża dzielnica Krakowa o socrealistycznej zabudowie, powstała "
        "wokół dawnej Huty im. Sendzimira.",
    ),
]


def seed_localities(apps, schema_editor):
    ServiceLocality = apps.get_model("web", "ServiceLocality")

    existing_slugs = set(ServiceLocality.objects.values_list("slug", flat=True))
    to_create = []
    for order, (name, region_label, local_note) in enumerate(LOCALITIES):
        slug = polish_slugify(name)
        if slug in existing_slugs:
            continue
        to_create.append(
            ServiceLocality(
                name=name,
                slug=slug,
                region_label=region_label,
                local_note=local_note,
                order=order,
                is_active=True,
            )
        )
    ServiceLocality.objects.bulk_create(to_create)


def remove_localities(apps, schema_editor):
    ServiceLocality = apps.get_model("web", "ServiceLocality")
    slugs = [polish_slugify(name) for name, _, _ in LOCALITIES]
    ServiceLocality.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0124_servicelocality"),
    ]

    operations = [
        migrations.RunPython(seed_localities, remove_localities),
    ]
