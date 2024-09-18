import stripe
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from web.functions import send_email_order_status
from web.models.orders import Order
from web.models.payments import Payment

from .serializers import PaymentMethodsSerializer


class PaymentMethodsView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PaymentMethodsSerializer

    @swagger_auto_schema(
        operation_description="Deliveries",
        responses={200: PaymentMethodsSerializer()},
    )
    def get(self, request, *args, **kwargs):
        payment_methods = Payment.objects.filter(is_active=True)
        serializer = self.get_serializer(payment_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        event = None

        stripe.api_key = settings.STRIPE_SECRET_KEY
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            print("⚠️  Webhook error while parsing basic request." + str(e))
            return HttpResponseBadRequest()
        except stripe.error.SignatureVerificationError as e:
            print("⚠️  Webhook signature verification failed." + str(e))
            return HttpResponseBadRequest()

        # Handle the event
        if event["type"] == "checkout.session.completed":
            checkout_session = event["data"]["object"]
            print(
                "Payment for {} succeeded".format(
                    checkout_session["amount_total"]
                )
            )

            order_uid = checkout_session["metadata"]["order_uid"]
            payment_status = checkout_session["payment_status"]
            try:
                order = Order.objects.get(uid=order_uid)
                if payment_status == "paid":
                    order.status = 3
                    order.is_paid = True
                    order.payment_date = timezone.now()
                    send_email_order_status(order)
                else:
                    order.status = 4
                order.save()
            except Order.DoesNotExist:
                pass

        return JsonResponse({"success": True})


payment_methods = PaymentMethodsView.as_view()
webhook = StripeWebhookView.as_view()
