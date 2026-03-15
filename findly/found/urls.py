from django.urls import path
from . import views

app_name = "found"

urlpatterns = [
    # ── Your original routes ──────────────────────────────────
    path("admin/",        views.adminDashboardView,  name="admin_dashboard"),
    path("owner/",        views.ownerDashboardView,  name="owner_dashboard"),
    path("finder/",       views.finderDashboardView, name="finder_dashboard"),
    path('review-match/', views.reviewMatchView,     name='review_match'),

    # ── New: Admin resolve a match (verify or reject) ─────────
    path('match/<uuid:match_id>/<str:action>/', views.adminResolveMatchView, name='resolve_match'),
]
