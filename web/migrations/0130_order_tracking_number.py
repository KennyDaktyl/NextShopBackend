from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0129_service_locality_inflection"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="tracking_number",
            field=models.CharField(
                blank=True,
                max_length=64,
                null=True,
                verbose_name="Numer przesyłki InPost",
            ),
        ),
    ]
