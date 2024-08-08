from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web"

    def ready(self):
        import web.categories.signals
        import web.front.signals
        import web.images.signals
        import web.products.signals
