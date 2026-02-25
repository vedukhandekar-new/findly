from django.contrib import admin
from django.urls import path,include
from . import views

app_name = "core"

urlpatterns = [
    path('signup/',views.userSignupView,name='signup'),
    path('login/',views.userLoginView,name='login')
    
]