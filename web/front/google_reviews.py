"""Opinie z wizytówki Google „Serwis w Rybnej” (Places API New) dla strony głównej.

- Pobieramy wyłącznie jedną wizytówkę: GOOGLE_PLACE_ID z env. Endpoint nie przyjmuje
  parametrów, a odpowiedź z innym id jest odrzucana.
- Koszty: cache 6 h + twardy limit zapytań w miesiącu (GooglePlacesApiUsage w bazie,
  wspólny dla wszystkich workerów gunicorna). Pole `reviews` to pakiet
  „Enterprise + Atmosphere” – 1000 zapytań/mies. gratis, potem 25 USD za 1000.
- Zgodnie z warunkami Google opinii nie zapisujemy w bazie ani plikach: tylko krótki
  cache w pamięci (django.core.cache). Klucz API nie trafia do logów ani do odpowiedzi.
"""

import logging
import re

import requests
from django.conf import settings
from django.core.cache import cache
from django.db.models import F
from django.utils import timezone

from web.models.google_places import GooglePlacesApiUsage

logger = logging.getLogger(__name__)

CACHE_KEY = "google_reviews_v1"
CACHE_TIMEOUT = 6 * 3600
# Po błędzie ponawiamy najwcześniej po godzinie (każda próba liczy się do limitu).
ERROR_CACHE_TIMEOUT = 3600
REQUEST_TIMEOUT = 5
PLACES_URL = "https://places.googleapis.com/v1/places/{place_id}"
PLACE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,}$")
FIELD_MASK = "id,rating,userRatingCount,googleMapsUri,googleMapsLinks.reviewsUri,reviews"


def empty_reviews():
    return {"rating": None, "userRatingCount": 0, "reviews": []}


def get_google_reviews():
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    data = fetch_google_reviews()
    timeout = CACHE_TIMEOUT if data is not None else ERROR_CACHE_TIMEOUT
    data = data if data is not None else empty_reviews()
    cache.set(CACHE_KEY, data, timeout)
    return data


def reserve_api_call():
    """Atomowo zwiększa licznik zapytań w bieżącym miesiącu (UTC), o ile nie osiągnięto limitu."""
    month = timezone.now().strftime("%Y-%m")
    limit = settings.GOOGLE_PLACES_MONTHLY_LIMIT
    GooglePlacesApiUsage.objects.get_or_create(month=month)
    updated = GooglePlacesApiUsage.objects.filter(month=month, requests__lt=limit).update(
        requests=F("requests") + 1, modified_date=timezone.now()
    )
    return updated == 1


def fetch_google_reviews():
    """Zwraca dane do API albo None przy braku konfiguracji, limicie lub błędzie."""
    api_key = getattr(settings, "GOOGLE_PLACES_API_KEY", "")
    place_id = getattr(settings, "GOOGLE_PLACE_ID", "")
    if not api_key or not place_id:
        logger.warning("Opinie Google: brak GOOGLE_PLACES_API_KEY lub GOOGLE_PLACE_ID.")
        return None
    if not PLACE_ID_RE.match(place_id):
        logger.warning("Opinie Google: GOOGLE_PLACE_ID ma niepoprawny format.")
        return None

    if not reserve_api_call():
        logger.warning(
            "Opinie Google: osiągnięto miesięczny limit %s zapytań – do końca miesiąca bez zapytań.",
            settings.GOOGLE_PLACES_MONTHLY_LIMIT,
        )
        return None

    try:
        response = requests.get(
            PLACES_URL.format(place_id=place_id),
            params={"languageCode": "pl"},
            headers={"X-Goog-Api-Key": api_key, "X-Goog-FieldMask": FIELD_MASK},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.RequestException as exc:
        # Sam typ wyjątku: komunikat mógłby zawierać nagłówki/URL żądania.
        logger.warning("Opinie Google: błąd połączenia (%s).", type(exc).__name__)
        return None

    if response.status_code != 200:
        logger.warning("Opinie Google: Places API zwróciło HTTP %s.", response.status_code)
        return None

    try:
        place = response.json()
    except ValueError:
        logger.warning("Opinie Google: niepoprawny JSON z Places API.")
        return None

    if place.get("id") != place_id:
        logger.warning("Opinie Google: odpowiedź nie dotyczy wizytówki z GOOGLE_PLACE_ID – odrzucona.")
        return None

    return serialize_place(place)


def serialize_place(place):
    google_maps_uri = place.get("googleMapsUri")
    reviews_uri = (place.get("googleMapsLinks") or {}).get("reviewsUri") or google_maps_uri
    reviews = []
    for review in place.get("reviews") or []:
        text = (review.get("originalText") or {}).get("text") or (review.get("text") or {}).get("text")
        if review.get("rating") != 5 or not (text or "").strip():
            continue
        author = review.get("authorAttribution") or {}
        reviews.append(
            {
                "rating": review.get("rating"),
                "text": text,
                "relativePublishTimeDescription": review.get("relativePublishTimeDescription"),
                "authorName": author.get("displayName"),
                "authorUri": author.get("uri"),
                "authorPhotoUri": author.get("photoUri"),
                "googleMapsUri": review.get("googleMapsUri"),
                "flagContentUri": review.get("flagContentUri"),
            }
        )
    return {
        "rating": place.get("rating"),
        "userRatingCount": place.get("userRatingCount") or 0,
        "googleMapsUri": google_maps_uri,
        "reviewsUri": reviews_uri,
        "reviews": reviews,
    }
