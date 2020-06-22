from django.urls import re_path, path
from . import views
from utils.ssl import ssl_handler

urlpatterns = [
    re_path(r'^(?P<checkout_type>[\w-]+)$', views.show_checkout, ssl_handler(), name='show_checkout'),
    re_path(r'^receipt/$', views.receipt, ssl_handler(), name='checkout_receipt'),
]
