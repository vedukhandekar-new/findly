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
    path('manage-users/', views.manageUsersView, name='manage_users'),
    path('block-item/<uuid:pk>/',   views.blockItemView,   name='block_item'),
    path('unblock-item/<uuid:pk>/', views.unblockItemView, name='unblock_item'),
    path('flagged-items/',          views.flaggedItemsView, name='flagged_items'),
]
