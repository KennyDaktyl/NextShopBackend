"""GET /api/front/google-reviews: tylko opinie 5★ z tekstem w kolejności Google,
pusta lista przy braku konfiguracji lub błędzie, klucz API nigdy w odpowiedzi."""

import json
from unittest import mock

import requests
from django.core.cache import cache
from django.test import TestCase, override_settings

from web.front.google_reviews import CACHE_KEY
from web.models.google_places import GooglePlacesApiUsage

API_KEY = "test-klucz-nie-prawdziwy-123"
EMPTY = {"rating": None, "userRatingCount": 0, "reviews": []}


def review(rating, text, name, original=True):
    body = {"text": text, "languageCode": "pl"}
    return {
        "rating": rating,
        ("originalText" if original else "text"): body,
        "relativePublishTimeDescription": "2 tygodnie temu",
        "authorAttribution": {
            "displayName": name,
            "uri": f"https://maps.google.com/contrib/{name}",
            "photoUri": f"https://lh3.googleusercontent.com/{name}",
        },
        "googleMapsUri": f"https://maps.google.com/review/{name}",
        "flagContentUri": f"https://maps.google.com/flag/{name}",
    }


PLACE_ID = "ChIJtestSerwisWRybnej"
PLACE = {
    "id": PLACE_ID,
    "rating": 4.9,
    "userRatingCount": 23,
    "googleMapsUri": "https://maps.google.com/?cid=1",
    "googleMapsLinks": {"reviewsUri": "https://maps.google.com/reviews?cid=1"},
    "reviews": [
        review(5, "Klucz do Skody Octavii, Ruczaj – szybko.", "Anna"),
        review(4, "Dobrze, ale czekałem.", "Bartek"),
        review(5, "   ", "Pusty"),
        review(5, "Pilot do bramy działa.", "Celina", original=False),
    ],
}


def ok_response(payload):
    response = mock.Mock(status_code=200)
    response.json.return_value = payload
    return response


@override_settings(GOOGLE_PLACES_API_KEY=API_KEY, GOOGLE_PLACE_ID=PLACE_ID, GOOGLE_PLACES_MONTHLY_LIMIT=900)
class GoogleReviewsTests(TestCase):
    url = "/api/front/google-reviews"

    def setUp(self):
        cache.delete(CACHE_KEY)
        self.addCleanup(cache.delete, CACHE_KEY)

    @mock.patch("web.front.google_reviews.requests.get")
    def test_only_five_star_reviews_with_text_in_google_order(self, get):
        get.return_value = ok_response(PLACE)
        data = self.client.get(self.url).json()

        self.assertEqual([r["authorName"] for r in data["reviews"]], ["Anna", "Celina"])
        self.assertEqual(data["reviews"][0]["text"], "Klucz do Skody Octavii, Ruczaj – szybko.")
        self.assertEqual(data["reviews"][1]["text"], "Pilot do bramy działa.")
        self.assertEqual(data["rating"], 4.9)
        self.assertEqual(data["userRatingCount"], 23)
        self.assertEqual(data["reviewsUri"], "https://maps.google.com/reviews?cid=1")
        self.assertEqual(
            set(data["reviews"][0]),
            {"rating", "text", "relativePublishTimeDescription", "authorName", "authorUri",
             "authorPhotoUri", "googleMapsUri", "flagContentUri"},
        )
        _args, kwargs = get.call_args
        self.assertEqual(kwargs["headers"]["X-Goog-Api-Key"], API_KEY)
        self.assertEqual(kwargs["timeout"], 5)

        # Drugie wywołanie z cache – bez kolejnego zapytania do Google.
        self.client.get(self.url)
        self.assertEqual(get.call_count, 1)

    @mock.patch("web.front.google_reviews.requests.get")
    def test_reviews_uri_falls_back_to_place_uri(self, get):
        get.return_value = ok_response({**PLACE, "googleMapsLinks": {}})
        data = self.client.get(self.url).json()
        self.assertEqual(data["reviewsUri"], PLACE["googleMapsUri"])

    @override_settings(GOOGLE_PLACES_API_KEY="")
    @mock.patch("web.front.google_reviews.requests.get")
    def test_missing_api_key_returns_empty_without_request(self, get):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY)
        get.assert_not_called()

    @mock.patch("web.front.google_reviews.requests.get")
    def test_http_error_returns_empty(self, get):
        get.return_value = mock.Mock(status_code=403)
        with self.assertLogs("web.front.google_reviews", "WARNING") as logs:
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), EMPTY)
        self.assertNotIn(API_KEY, "\n".join(logs.output))

    @mock.patch("web.front.google_reviews.requests.get")
    def test_timeout_returns_empty_and_retries_after_hour(self, get):
        get.side_effect = requests.exceptions.Timeout(f"timeout key={API_KEY}")
        with mock.patch("web.front.google_reviews.cache.set") as cache_set, \
                self.assertLogs("web.front.google_reviews", "WARNING") as logs:
            response = self.client.get(self.url)
        self.assertEqual(response.json(), EMPTY)
        self.assertEqual(cache_set.call_args[0][2], 3600)
        self.assertNotIn(API_KEY, "\n".join(logs.output))

    @mock.patch("web.front.google_reviews.requests.get")
    def test_api_key_never_in_response(self, get):
        get.return_value = ok_response(PLACE)
        body = self.client.get(self.url).content.decode()
        self.assertNotIn(API_KEY, body)
        self.assertNotIn(API_KEY, json.dumps(cache.get(CACHE_KEY)))

    @mock.patch("web.front.google_reviews.requests.get")
    def test_requests_only_own_place_and_counts_usage(self, get):
        get.return_value = ok_response(PLACE)
        self.client.get(self.url)
        url = get.call_args[0][0]
        self.assertEqual(url, f"https://places.googleapis.com/v1/places/{PLACE_ID}")
        self.assertEqual(GooglePlacesApiUsage.objects.get().requests, 1)

    @mock.patch("web.front.google_reviews.requests.get")
    def test_other_place_in_response_is_rejected(self, get):
        get.return_value = ok_response({**PLACE, "id": "ChIJinnaFirma123"})
        self.assertEqual(self.client.get(self.url).json(), EMPTY)

    @override_settings(GOOGLE_PLACE_ID="ChIJ/../../inne")
    @mock.patch("web.front.google_reviews.requests.get")
    def test_invalid_place_id_format_makes_no_request(self, get):
        self.assertEqual(self.client.get(self.url).json(), EMPTY)
        get.assert_not_called()

    @mock.patch("web.front.google_reviews.requests.get")
    def test_monthly_limit_blocks_requests(self, get):
        from django.utils import timezone

        GooglePlacesApiUsage.objects.create(month=timezone.now().strftime("%Y-%m"), requests=900)
        self.assertEqual(self.client.get(self.url).json(), EMPTY)
        get.assert_not_called()
        self.assertEqual(GooglePlacesApiUsage.objects.get().requests, 900)

    @mock.patch("web.front.google_reviews.requests.get")
    def test_cache_lasts_six_hours(self, get):
        get.return_value = ok_response(PLACE)
        with mock.patch("web.front.google_reviews.cache.set") as cache_set:
            self.client.get(self.url)
        self.assertEqual(cache_set.call_args[0][2], 6 * 3600)
