"""POST /api/front/contact-email: opcjonalne zdjęcie (np. klucza) trafia do maila jako załącznik;
bez zdjęcia formularz działa jak dotąd; plik niebędący grafiką lub za duży jest odrzucany;
JSON (zamówienia pieczątek) dalej działa."""

from io import BytesIO
from unittest import mock

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

URL = "/api/front/contact-email"
FORM = {"title": "Dorobienie klucza", "email": "klient@example.com", "message": "Czy dorobicie taki klucz?"}


def jpeg(name="klucz.jpg", size=(80, 60)):
    buf = BytesIO()
    Image.new("RGB", size, "gray").save(buf, "JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST_USER="serwis@example.com",
)
class ContactAttachmentTests(TestCase):
    def test_photo_is_attached_to_email(self):
        response = self.client.post(URL, {**FORM, "attachment": jpeg()})

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, FORM["title"])
        self.assertEqual(len(message.attachments), 1)
        filename, content, mimetype = message.attachments[0]
        self.assertEqual(filename, "zalacznik-klucz.jpg")
        self.assertEqual(mimetype, "image/jpeg")
        Image.open(BytesIO(content)).verify()  # poprawny plik graficzny

    def test_form_without_photo_still_works(self):
        response = self.client.post(URL, FORM)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox[0].attachments, [])

    def test_json_request_still_works(self):
        response = self.client.post(URL, FORM, content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_non_image_file_is_rejected(self):
        fake = SimpleUploadedFile("klucz.jpg", b"to nie jest obrazek", content_type="image/jpeg")
        response = self.client.post(URL, {**FORM, "attachment": fake})
        self.assertEqual(response.status_code, 400)
        self.assertIn("attachment", response.json())
        self.assertEqual(mail.outbox, [])

    @mock.patch("web.front.serializers.MAX_PHOTO_SIZE", 100)
    def test_too_large_photo_is_rejected(self):
        response = self.client.post(URL, {**FORM, "attachment": jpeg(size=(400, 400))})
        self.assertEqual(response.status_code, 400)
        self.assertIn("za duże", str(response.json()["attachment"]))
        self.assertEqual(mail.outbox, [])

    def test_unsafe_filename_is_sanitized(self):
        self.client.post(URL, {**FORM, "attachment": jpeg(name="../../etc/zdjęcie klucza.jpg")})
        filename = mail.outbox[0].attachments[0][0]
        self.assertNotIn("/", filename)
        self.assertTrue(filename.startswith("zalacznik-"))

    def test_plain_contact_message_has_no_ink_color(self):
        self.client.post(URL, FORM)
        message = mail.outbox[0]
        self.assertNotIn("Kolor tuszu", message.body)
        self.assertNotIn("Kolor tuszu", message.alternatives[0][0])

    def test_stamp_order_keeps_ink_color(self):
        stamp = {**FORM, "stamp_design": [{"text": "FIRMA SP. Z O.O.", "font": "Arial", "size": 12, "bold": True, "italic": False}], "stamp_color": "red"}
        response = self.client.post(URL, stamp, content_type="application/json")
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn("Kolor tuszu", mail.outbox[0].alternatives[0][0])
