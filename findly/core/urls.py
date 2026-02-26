from django.contrib import admin
from django.urls import path,include
from . import views

app_name = "core"

urlpatterns = [
    path('signup/',views.userSignupView,name='signup'),
    path('login/',views.userLoginView,name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('finder/', views.finder_dashboard, name='finder_dashboard'),
    path('owner/', views.finder_dashboard, name='owner_dashboard'),
    
]