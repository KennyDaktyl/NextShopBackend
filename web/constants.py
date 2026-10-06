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
    (2, _("Płatności anulowana")),
    (3, _("Opłacone")),
    (4, _("Trwa weryfikacja płatności")),
    (5, _("Do zapłaty")),
    (6, _("Płatność nieudana")),
    (7, _("Błąd płatności Stripe")),
    (8, _("W trakcie realizacji")),
    (9, _("W dostawie")),
    (10, _("Dostarczone")),
    (11, _("Zwrócone")),
    (12, _("Gotowe do odbioru")),
    (13, _("Zrealizowane")),
    (14, _("Anulowane")),
)

VARIANT_COLORS = (
    (0, _("Brak koloru")),
    (1, _("Biały")),
    (2, _("Szary")),
    (3, _("Czerwony")),
    (4, _("Niebieski")),
    (5, _("Zielony")),
    (6, _("Żółty")),
    (7, _("Pomarańczowy")),
    (8, _("Brązowy")),
    (9, _("Różowy")),
    (10, _("Fioletowy")),
    (11, _("Beżowy")),
    (12, _("Czarny")),
)


# Zmiana statusu na jeden z tych (Opłacone, W dostawie, Gotowe do odbioru,
# Zrealizowane, Anulowane) wysyła klientowi e-mail - tylko dla zamówień
# z wysyłką (nie odbiór osobisty). Inne zmiany statusu - bez maila.
STATUS_FOR_SEND_EMAIL = [3, 9, 12, 13, 14]
# Statusy ustawiane przez sklep (admin, webhook Stripe). Frontend klienta
# (np. odświeżenie strony po złożeniu zamówienia) nie może ich już zmienić.
STATUS_LOCKED_FOR_CLIENT = [3, 5, 9, 10, 11, 12, 13, 14]
STATUS_TO_MAKE_INVOICE = [3, 5, 8, 9, 12, 13]
