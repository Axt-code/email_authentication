from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
   path('', home, name= "home"),
   path('login/', login_attempt, name = "login"),
   path('register/', register, name = "register"),
   path('token/', token_send, name="token_send"),
   path('verify/<auth_token>', verify, name='verify'),
   path('error/', error_page, name="error"),
   path('forget_pass/', forget_pass, name="forget_pass"),
   path('change_pass/<auth_token>', change_pass, name='change_pass'),

]