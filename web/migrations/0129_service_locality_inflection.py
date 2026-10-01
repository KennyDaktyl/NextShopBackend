from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0128_seed_footer_links"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicelocality",
            name="name_to",
            field=models.CharField(
                blank=True,
                default="",
                max_length=120,
                verbose_name="Odmiana: dokąd (np. „do Alwerni”, „na Krowodrzę”)",
            ),
        ),
        migrations.AddField(
            model_name="servicelocality",
            name="name_in",
            field=models.CharField(
                blank=True,
                default="",
                max_length=120,
                verbose_name="Odmiana: gdzie (np. „w Alwerni”, „na Krowodrzy”)",
            ),
        ),
    ]
