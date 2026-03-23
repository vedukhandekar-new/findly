from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────
    path('signup/',     views.userSignupView,  name='signup'),
    path('login/',      views.userLoginView,   name='login'),
    path('logout/',     views.user_logout,     name='logout'),
    path('',            views.home_view,       name='home'),

    # ── OTP Verify ────────────────────────────────────────
    path('verify-otp/', views.verifyOtpView,   name='verify_otp'),
    path('resend-otp/', views.resendOtpView,   name='resend_otp'),

    # ── Forgot Password ───────────────────────────────────
    path('forgot-password/',            views.forgotPasswordView, name='forgot_password'),
    path('forgot-password/verify-otp/', views.forgotOtpView,      name='forgot_otp'),
    path('forgot-password/reset/',      views.resetPasswordView,  name='reset_password'),

    # ── Profile ───────────────────────────────────────────
    path('profile/', views.profile_view, name='profile'),

    # ── Items ─────────────────────────────────────────────
    path('report/lost/',            views.report_lost_view,      name='report_lost'),
    path('report/found/',           views.report_found_view,     name='report_found'),
    path('item/<uuid:pk>/',         views.item_detail_view,      name='item_detail'),
    path('my-items/',               views.my_items_view,         name='my_items'),
    path('item/<uuid:pk>/recover/', views.confirm_recovery_view, name='confirm_recovery'),

    # ── Search ────────────────────────────────────────────
    path('search/', views.search_items_view, name='search_items'),

    # ── Messaging ─────────────────────────────────────────
    path('match/<uuid:match_id>/chat/', views.match_chat_view, name='match_chat'),

    # ── Notifications ─────────────────────────────────────
    path('notifications/',   views.notifications_view,     name='notifications'),
    path('api/notif-count/', views.notification_count_api, name='notif_count_api'),

    # ── Reviews ───────────────────────────────────────────
    path('review/<uuid:item_id>/user/<uuid:target_user_id>/', views.submit_review_view, name='submit_review'),

    # ── Payments ──────────────────────────────────────────
    path('payment/<uuid:match_id>/',         views.payment_view,         name='payment'),
    path('payment/<uuid:match_id>/process/', views.process_payment_view, name='process_payment'),
    path('payment/<uuid:match_id>/success/', views.payment_success_view, name='payment_success'),
    path('test-404/', views.custom_404, name='test_404'),
    path('item/<uuid:pk>/flag/', views.flag_item_view, name='flag_item'),
]