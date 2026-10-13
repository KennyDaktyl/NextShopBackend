"""E-maile zamówień: każde złożone zamówienie musi dać potwierdzenie
(sklep + klient), dokładnie raz, dla każdej kombinacji dostawy i płatności.
"""
from decimal import Decimal
from unittest import mock

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from web.models.accounts import Profile
from web.models.deliveries import Delivery
from web.models.orders import Order
from web.models.payments import Payment

SHOP_EMAIL = "sklep@example.com"
CLIENT_EMAIL = "klient@example.com"

CART_ITEM = {
    "id": 999999,
    "name": "Pieczątka testowa",
    "slug": "pieczatka-testowa",
    "price": "50.00",
    "quantity": 1,
    "url": "/produkt/pieczatka-testowa",
    "free_delivery": False,
}


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST_USER=SHOP_EMAIL,
    FREE_DELIVERY_THRESHOLD=100000,
)
class OrderEmailTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.courier = Delivery.objects.create(name="Kurier inpost", price=Decimal("15"), price_promo=Decimal("0"))
        cls.locker = Delivery.objects.create(name="Inpost Paczkomaty", price=Decimal("12"), price_promo=Decimal("0"), inpost_box=True)
        cls.pickup = Delivery.objects.create(name="Odbiór osobisty", price=Decimal("0"), price_promo=Decimal("0"), in_store_pickup=True)

        cls.online = Payment.objects.create(name="Przelew online", price=Decimal("0"), price_promo=Decimal("0"), payment_online=True, order=0)
        cls.transfer = Payment.objects.create(name="Przelew bankowy", price=Decimal("0"), price_promo=Decimal("0"), bank_transfer=True, order=1)
        cls.cash = Payment.objects.create(name="Gotówka", price=Decimal("0"), price_promo=Decimal("0"), pickup_only=True, order=2)
        cls.card = Payment.objects.create(name="Płatność kartą", price=Decimal("0"), price_promo=Decimal("0"), pickup_only=True, order=3)
        cls.cod = Payment.objects.create(name="Płatność przy odbiorze", price=Decimal("5"), price_promo=Decimal("0"), payment_on_delivery=True, order=4)

    def setUp(self):
        self.api = APIClient()

    # --- helpers --------------------------------------------------------------------------------

    def place_order(self, delivery, payment, client=None):
        if client is not None:
            self.api.force_authenticate(client)
        session = self.api.session
        session["cart"] = {"id": "test", "cart_items": [dict(CART_ITEM)], "free_delivery": False}
        session.save()
        payload = {
            "client_name": "Jan Kowalski",
            "client_email": CLIENT_EMAIL,
            "client_mobile": "500600700",
            "delivery_price": str(delivery.price),
            "payment_price": str(payment.price),
            "cart_items_price": "50.00",
            "amount": "50.00",
            "delivery_method": str(delivery.id),
            "payment_method": str(payment.id),
            "cart_items": [dict(CART_ITEM)],
            "make_invoice": False,
        }
        with self.captureOnCommitCallbacks(execute=True):
            response = self.api.post("/api/orders/create/", payload, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        return Order.objects.get(uid=response.data["order_uid"])

    def frontend_status(self, order, status):
        with self.captureOnCommitCallbacks(execute=True):
            self.api.post(f"/api/orders/update-status/{order.uid}/", {"status": status}, format="json")

    def save(self, order, **fields):
        order.refresh_from_db()
        for key, value in fields.items():
            setattr(order, key, value)
        with self.captureOnCommitCallbacks(execute=True):
            order.save()

    def recipients(self):
        return sorted(to for m in mail.outbox for to in m.to)

    def assert_confirmation_sent(self, order):
        self.assertEqual(self.recipients(), sorted([SHOP_EMAIL, CLIENT_EMAIL]))
        subjects = [m.subject for m in mail.outbox]
        self.assertTrue(any(s.startswith(f"Potwierdzenie zamówienia nr {order.order_number}") for s in subjects), subjects)
        self.assertTrue(any(s.startswith(f"Nowe zamówienie nr {order.order_number}") for s in subjects), subjects)
        order.refresh_from_db()
        self.assertTrue(order.confirmation_email_sent)

    # --- płatności offline: potwierdzenie od razu po złożeniu -----------------------------------

    def test_offline_payments_send_confirmation_on_create_for_every_delivery(self):
        combos = [
            (self.courier, self.transfer),
            (self.locker, self.transfer),
            (self.pickup, self.transfer),
            (self.pickup, self.cash),
            (self.pickup, self.card),
            (self.courier, self.cod),
            (self.locker, self.cod),
            (self.pickup, self.cod),
        ]
        for delivery, payment in combos:
            with self.subTest(delivery=delivery.name, payment=payment.name):
                mail.outbox = []
                order = self.place_order(delivery, payment)
                self.assertEqual(order.status, 5)
                self.assert_confirmation_sent(order)

                # Frontend po złożeniu wysyła jeszcze 5 i 4/8 - bez kolejnych maili.
                self.frontend_status(order, 5)
                self.frontend_status(order, 4 if payment.bank_transfer else 8)
                self.assertEqual(len(mail.outbox), 2)

    def test_bank_transfer_confirmation_contains_transfer_details(self):
        order = self.place_order(self.courier, self.transfer)
        client_mail = next(m for m in mail.outbox if m.to == [CLIENT_EMAIL])
        html = client_mail.alternatives[0][0]
        self.assertIn("21 1020 2906 0000 1702 0373 8333", html)
        self.assertIn(f"Zamówienie #{order.order_number}", html)

    def test_pickup_only_payment_with_shipping_falls_back_to_online(self):
        # Gotówka/karta tylko przy odbiorze - przy wysyłce backend wymusza
        # płatność online, więc potwierdzenie przychodzi po opłaceniu.
        order = self.place_order(self.courier, self.cash)
        self.assertEqual(order.payment_method, self.online)
        self.assertEqual(len(mail.outbox), 0)
        self.save(order, status=3, is_paid=True)
        self.assert_confirmation_sent(order)

    # --- płatność online (Stripe) ---------------------------------------------------------------

    def test_online_payment_confirmation_after_webhook_paid(self):
        for delivery in (self.courier, self.locker, self.pickup):
            with self.subTest(delivery=delivery.name):
                mail.outbox = []
                order = self.place_order(delivery, self.online)
                self.assertEqual(order.status, 0)
                self.frontend_status(order, 1)  # przekierowanie do Stripe
                self.assertEqual(len(mail.outbox), 0)

                self.save(order, status=3, is_paid=True)  # webhook
                self.assert_confirmation_sent(order)

                self.save(order)  # kolejny zapis bez zmian
                self.assertEqual(len(mail.outbox), 2)

    def test_online_payment_success_page_before_webhook(self):
        order = self.place_order(self.courier, self.online)
        self.frontend_status(order, 1)
        # Strona sukcesu przed webhookiem: 3 -> 4 (płatność niepotwierdzona).
        self.frontend_status(order, 3)
        order.refresh_from_db()
        self.assertEqual(order.status, 4)
        self.assert_confirmation_sent(order)

        mail.outbox = []
        self.save(order, status=3, is_paid=True)  # webhook
        self.assertEqual(self.recipients(), sorted([SHOP_EMAIL, CLIENT_EMAIL]))
        self.assertTrue(all("Opłacone" in m.subject for m in mail.outbox))

    def test_abandoned_or_failed_online_payment_sends_nothing(self):
        for status in (1, 2, 6, 7):
            with self.subTest(status=status):
                mail.outbox = []
                order = self.place_order(self.courier, self.online)
                self.frontend_status(order, status)
                self.assertEqual(len(mail.outbox), 0)

    # --- zmiany statusu po potwierdzeniu --------------------------------------------------------

    def test_status_changes_after_confirmation_for_shipping(self):
        order = self.place_order(self.courier, self.transfer)
        for status in (3, 9, 13):
            mail.outbox = []
            self.save(order, status=status, is_paid=status != 9 or order.is_paid)
            self.assertEqual(self.recipients(), sorted([SHOP_EMAIL, CLIENT_EMAIL]), status)

    def test_unconfirmed_order_marked_paid_by_shop_gets_one_confirmation(self):
        # Zamówienie bez potwierdzenia (np. nieudana wysyłka), które sklep
        # oznacza jako opłacone: potwierdzenie zamiast maila o statusie,
        # a nie oba naraz.
        order = self.place_order(self.courier, self.transfer)
        Order.objects.filter(pk=order.pk).update(confirmation_email_sent=False)
        mail.outbox = []
        self.save(order, status=3, is_paid=True)
        self.assert_confirmation_sent(order)
        self.assertEqual(len(mail.outbox), 2)

    # --- odbiorcy -------------------------------------------------------------------------------

    def test_logged_in_client_without_marketing_consent_gets_confirmation(self):
        user = User.objects.create_user("jan", CLIENT_EMAIL, "haslo-testowe-123")
        Profile.objects.update_or_create(user=user, defaults={"send_emails": False})
        order = self.place_order(self.pickup, self.transfer, client=user)
        self.assert_confirmation_sent(order)

    def test_email_notification_off_still_notifies_shop(self):
        order = self.place_order(self.courier, self.online)
        Order.objects.filter(pk=order.pk).update(email_notification=False)
        self.save(order, status=3, is_paid=True)
        self.assertEqual(self.recipients(), [SHOP_EMAIL])

    def test_failed_send_is_retried_on_next_save(self):
        order = self.place_order(self.courier, self.online)
        with mock.patch("django.core.mail.EmailMultiAlternatives.send", side_effect=OSError("SMTP down")):
            self.save(order, status=4)
        order.refresh_from_db()
        self.assertFalse(order.confirmation_email_sent)
        self.assertEqual(len(mail.outbox), 0)

        self.save(order, status=3, is_paid=True)
        self.assert_confirmation_sent(order)

    def test_failure_for_one_recipient_does_not_block_the_other(self):
        order = self.place_order(self.courier, self.online)
        real_send = mail.EmailMultiAlternatives.send

        def flaky_send(message, *args, **kwargs):
            if message.to == [SHOP_EMAIL]:
                raise OSError("SMTP down")
            return real_send(message, *args, **kwargs)

        with mock.patch("django.core.mail.EmailMultiAlternatives.send", autospec=True, side_effect=flaky_send):
            self.save(order, status=3, is_paid=True)
        self.assertEqual(self.recipients(), [CLIENT_EMAIL])
