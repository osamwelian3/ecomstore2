from ecomstore import settings


def ssl_handler():
    if settings.SSL_ON:
        return {'SSL': True}
    if not settings.SSL_ON:
        return {}
