from django.db import models

from web.constants import PROFILE_STATUS
from web.models.prices import PriceGroup


class Profile(models.Model):
    user = models.OneToOneField(
        "auth.User",
        verbose_name="User",
        on_delete=models.CASCADE,
        db_index=True,
        related_name="profile",
    )
    status = models.IntegerField("Status", choices=PROFILE_STATUS, default=0)
    mobile = models.CharField("Mobile", max_length=15, blank=True, null=True)
    company = models.CharField(
        "Nazwa firmy", max_length=100, blank=True, null=True
    )
    nip = models.CharField("NIP", max_length=10, blank=True, null=True)
    address = models.CharField("Ulica", max_length=100, blank=True, null=True)
    house_number = models.CharField(
        "Numer domu", max_length=10, blank=True, null=True
    )
    local_number = models.CharField(
        "Numer lokalu", max_length=10, blank=True, null=True
    )
    city = models.CharField("Miasto", max_length=50, blank=True, null=True)
    postal_code = models.CharField(
        "Kod pocztowy", max_length=6, blank=True, null=True
    )
    inpost_code = models.CharField(
        "Kod paczkomatu InPost", max_length=10, blank=True, null=True
    )
    newsletter = models.BooleanField("Newsletter", default=False)

    price_group = models.ForeignKey(
        PriceGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        related_name="profiles",
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Profil użytkownika"
        verbose_name_plural = "Profile użytkowników"
        ordering = ["-user__pk"]
