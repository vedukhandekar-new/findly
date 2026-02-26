from django.urls import path
from . import views

app_name = "found"

urlpatterns = [
    path("admin/",views.adminDashboardView,name="admin_dashboard"),
    path("owner/",views.ownerDashboardView,name="owner_dashboard"),
    path("finder/",views.finderDashboardView,name="finder_dashboard")
]