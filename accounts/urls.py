# from django.conf.urls import defaults
# from django.conf.urls import *
# from ecomstore import settings
from django.urls import include, path, re_path
from utils.ssl import ssl_handler
from django.contrib.auth import views as auth_views
# from django.contrib.auth import views as auth_views, logout
from . import views


urlpatterns = [
    re_path(r'^register/$', views.register, ssl_handler(), name='register'),
    re_path(r'^my_account/$', views.my_account, ssl_handler(), name='my_account'),
    re_path(r'^order_details/(?P<order_id>[-\w]+)/$', views.order_details, ssl_handler(), name='order_details'),
    re_path(r'^order_info/$', views.order_info, ssl_handler(), name='order_info'),

    re_path(r'^login/$', auth_views.LoginView.as_view(), ssl_handler(), name='login'),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),

    re_path(r'^password_change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
    re_path(r'^password_change/done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
]
