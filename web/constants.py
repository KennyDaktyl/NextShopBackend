from django.utils.translation import gettext_lazy as _

PROFILE_STATUS = (
    (0, _("Klient")),
    (1, _("Konto firmowe")),
    (2, _("Admin")),
)

PAYMENT_METHOD = (
    (0, _("Przelew tradycyjny")),
    (1, _("Przelew online")),
    (2, _("Karta kredytowa")),
    (3, _("Gotówka")),
)

ORDER_STATUS = (
    (0, _("Nowe")),
    (1, _("W trakcie płatności")),
    (2, _("Opłacone")),
    (3, _("Do zapłaty")),
    (4, _("Płatność nieudana")),
    (5, _("W trakcie realizacji")),
    (6, _("W dostawie")),
    (7, _("Dostarczone")),
    (8, _("Zwrócone")),
    (9, _("Gotowe do odbioru")),
    (10, _("Zrealizowane")),
    (11, _("Anulowane")),
)
