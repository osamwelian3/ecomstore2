from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'^$', views.index, name='catalog_home'),
    re_path(r'^category/(?P<category_slug>[-\w]+)/$', views.show_category, name='catalog_category'),
    re_path(r'^product/(?P<product_slug>[-\w]+)/$', views.show_product, name='catalog_product'),
]
