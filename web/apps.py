from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "web"
    
    def ready(self):
        import web.products.signals
        import web.images.signals
        import web.categories.signals
