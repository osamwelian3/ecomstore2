"""ecomstore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from preview import views
from utils.ssl import ssl_handler

urlpatterns = [
    path('admin/', admin.site.urls, ssl_handler()),
    re_path(r'^catalog/$', views.home, ssl_handler(), name='homalog'),
    re_path(r'^', include('catalog.urls'), ssl_handler()),
    re_path(r'^cart/', include('cart.urls'), ssl_handler()),
    re_path(r'^checkout/', include('checkout.urls'), ssl_handler()),
    re_path(r'^api/v1/', include('mpesa_api.urls'), ssl_handler()),
    re_path(r'^myaccounts/', include('accounts.urls'), ssl_handler()),
]
handler404 = 'ecomstore.views.file_not_found_404'
