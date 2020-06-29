from django.urls import re_path, path
from . import views

urlpatterns = [
    re_path(r'^(?P<checkout_type>[\w-]+)$', views.show_checkout, name='show_checkout'),
    re_path(r'^receipt/$', views.receipt, name='checkout_receipt'),
]
