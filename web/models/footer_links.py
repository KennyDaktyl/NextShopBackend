from django.db import models


class FooterLink(models.Model):
    TYPE_PARTNER = "partner"
    TYPE_AUTHOR = "author"
    TYPE_CHOICES = (
        (TYPE_PARTNER, "Partner"),
        (TYPE_AUTHOR, "Twórca serwisu"),
    )

    name = models.CharField(verbose_name="Tekst linku", max_length=100)
    url = models.URLField(verbose_name="Adres URL")
    description = models.CharField(
        verbose_name="Opis (aria-label)", max_length=255, blank=True
    )
    link_type = models.CharField(
        verbose_name="Rodzaj",
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_PARTNER,
    )
    order = models.PositiveIntegerField(verbose_name="Kolejność", default=0)
    is_active = models.BooleanField(verbose_name="Aktywny", default=True)

    class Meta:
        ordering = ("order", "name")
        verbose_name = "Link w stopce"
        verbose_name_plural = "Linki w stopce"

    def __str__(self):
        return f"{self.name} ({self.get_link_type_display()})"
