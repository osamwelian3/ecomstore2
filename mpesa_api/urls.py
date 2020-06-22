from django.urls import path, re_path
from . import views


urlpatterns = [
    re_path(r'^access/token/$', views.getAccessToken, name='get_mpesa_access_token'),
    re_path(r'^online/lipa/$', views.lipa_na_mpesa_online, name='lipa_na_mpesa_online'),
    re_path(r'^c2b/register/$', views.register_urls, name='register_mpesa_validation'),
    re_path(r'^c2b/confirmation/$', views.confirmation, name='confirmation'),
    re_path(r'^c2b/validation/$', views.validation, name='validation'),
    re_path(r'^c2b/callback/$', views.call_back, name='call_back'),
    re_path(r'^query/lipa/(?P<cri>[\w-]+)/$', views.query_lipa, name='qlipa'),
    re_path(r'^c2b/transact/$', views.c2b, name='c2b'),
]
