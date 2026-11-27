from django.db import models


class GooglePlacesApiUsage(models.Model):
    """Licznik zapytań do Google Places API w miesiącu – twardy limit kosztów.

    Tylko liczba zapytań; treści opinii nie są nigdzie zapisywane (warunki Google).
    """

    month = models.CharField(verbose_name="Miesiąc (RRRR-MM, UTC)", max_length=7, unique=True)
    requests = models.PositiveIntegerField(verbose_name="Liczba zapytań", default=0)
    modified_date = models.DateTimeField(verbose_name="Ostatnie zapytanie", auto_now=True)

    class Meta:
        verbose_name = "Zużycie Google Places API"
        verbose_name_plural = "Zużycie Google Places API"
        ordering = ("-month",)

    def __str__(self):
        return f"{self.month}: {self.requests}"
