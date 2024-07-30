import logging

logger = logging.getLogger(__name__)

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Logowanie nagłówków żądania
        logger.info(f"Request Headers: {request.headers}")
        # Logowanie ciasteczek
        logger.info(f"Request Cookies: {request.COOKIES}")

        response = self.get_response(request)
        return response
