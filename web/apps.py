from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web"

    def ready(self):
        import web.articles.signals
        import web.categories.signals
        import web.deliveries.signals
        import web.front.signals
        import web.images.signals
        import web.orders.signals
        import web.payments.signals
        import web.products.signals
