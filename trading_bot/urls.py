"""
URL configuration for trading_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from . import views
from .consumers import PriceConsumer

urlpatterns = [

    path('admin/', admin.site.urls),
    path('register/', views.register_view, name="register"),
    path('login/', views.login_view, name="login"),
    path('home/',views.homepage, name='homepage'),
    path('',views.mainpage, name='mainpage'),
    path('about/',views.about),
    path('form_kline/',views.kline_view),
    path('trading_form/',views.bybit_data_view),
    path('get_taapi_data/', views.taapi_form, name='get_taapi_data'),
    path('fetch_taapi_data/', views.fetch_taapi_data, name='fetch_taapi_data'),

    path('place_order/', views.place_order, name='place_order'),
    path('place_sell_order/', views.place_sell_order, name='place_sell_order'),
    path('order_place/', views.order_form, name='order_place'),
    path('fetch_wallet_balance/', views.fetch_wallet_balance, name='fetch_wallet_balance'),
    path('api-form/', views.api_form_view, name='api_form')
]

