from django.urls import include, path
from web.views import *

app_name = "web"
urlpatterns = [
    path('', index, name="index"),
    path('login', login_view, name="login"),
    #path('second-factor', second_factor_login, name='second_factor_login'),
    path('register', register_view, name="register"),
    path('account', account_view, name="account"),
    path('logout', logout_view, name="logout"),
    path('marketplace', marketplace_view, name="marketplace"),
    path('trader/<uuid:fundID>', trader_view, name="trader")
]
