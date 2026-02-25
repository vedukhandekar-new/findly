from django.urls import path
from . import views

urlpatterns = [
    path("owner/",views.ownerDashboardView,name="owner_dashboard"),
    path("finder/",views.finderDashboardView,name="finder_dashboard")
]