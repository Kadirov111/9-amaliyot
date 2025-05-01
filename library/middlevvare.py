from django.utils import translation
from django.conf import settings

class LanguageMiddleware:
    """
    Til tanlash middleware.
    Accept-Language sarlavhasi orqali tilni o'rnatadi
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if language:
            # So'ralgan til bazada mavjud bo'lsa, o'rnat
            if language in [lang_code for lang_code, lang_name in settings.LANGUAGES]:
                translation.activate(language)
                request.LANGUAGE_CODE = translation.get_language()
            else:
                # Agar tilni topilmasa, standart tilni o'rnat
                translation.activate(settings.LANGUAGE_CODE)
                request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        else:
            # Agar so'ralgan til bo'lmasa, standart tilni o'rnat
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE

        response = self.get_response(request)
        return response