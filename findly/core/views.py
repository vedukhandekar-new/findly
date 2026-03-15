from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
from email.mime.image import MIMEImage
import os
import random

from .forms import (
    UserSignupForm, UserLoginForm, UserProfileForm,
    ReportLostItemForm, ReportFoundItemForm, ItemSearchForm,
    MessageForm, ReviewForm,
)
from .models import User, Item, Match, Message, Notification, Review
from .utils import run_matching_algorithm, send_notification


def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            user.otp_created_at = timezone.now()
            user.save()
            try:
                html_body = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Verify Your Email - Findly</title>
                </head>
                <body style="margin:0;padding:0;background-color:#09090B;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">

                    <!-- Wrapper -->
                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#09090B;padding:40px 20px;">
                        <tr>
                            <td align="center">
                                <table width="100%" max-width="560" cellpadding="0" cellspacing="0"
                                    style="max-width:560px;background-color:#121214;border-radius:20px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">

                                    <!-- Header -->
                                    <tr>
                                        <td style="background:linear-gradient(135deg,#1d4ed8,#4f46e5);padding:36px 40px;text-align:center;">
                                            <table cellpadding="0" cellspacing="0" style="margin:0 auto 16px;">
                                                <tr>
                                                    <td style="background:rgba(255,255,255,0.15);border-radius:14px;width:48px;height:48px;text-align:center;vertical-align:middle;">
                                                        <span style="font-size:22px;">🔍</span>
                                                    </td>
                                                </tr>
                                            </table>
                                            <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:800;letter-spacing:-0.5px;">Findly</h1>
                                            <p style="margin:6px 0 0;color:rgba(255,255,255,0.7);font-size:13px;font-weight:400;">Lost & Found Platform</p>
                                        </td>
                                    </tr>

                                    <!-- Body -->
                                    <tr>
                                        <td style="padding:36px 40px;">

                                            <!-- Greeting -->
                                            <h2 style="margin:0 0 8px;color:#f4f4f5;font-size:20px;font-weight:700;">
                                                Welcome, {user.first_name or 'there'} 👋
                                            </h2>
                                            <p style="margin:0 0 24px;color:#71717a;font-size:14px;line-height:1.6;">
                                                Thank you for joining <strong style="color:#a1a1aa;">Findly</strong> — your trusted platform for reporting and recovering lost items. We're excited to have you on board!
                                            </p>

                                            <!-- Divider -->
                                            <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 24px;">

                                            <!-- OTP Section -->
                                            <p style="margin:0 0 12px;color:#a1a1aa;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;">
                                                Your Verification Code
                                            </p>

                                            <!-- OTP Box -->
                                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                                                <tr>
                                                    <td style="background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(79,70,229,0.15));border:1px solid rgba(59,130,246,0.3);border-radius:14px;padding:24px;text-align:center;">
                                                        <p style="margin:0 0 8px;color:#93c5fd;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">One-Time Password</p>
                                                        <p style="margin:0;color:#ffffff;font-size:40px;font-weight:800;letter-spacing:12px;font-family:'Courier New',monospace;">{otp}</p>
                                                    </td>
                                                </tr>
                                            </table>

                                            <!-- Expiry Notice -->
                                            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                                                <tr>
                                                    <td style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:10px;padding:12px 16px;">
                                                        <p style="margin:0;color:#fbbf24;font-size:13px;">
                                                            ⏱ This code expires in <strong>10 minutes</strong>. Do not share it with anyone.
                                                        </p>
                                                    </td>
                                                </tr>
                                            </table>

                                            <!-- Divider -->
                                            <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 24px;">

                                            <!-- What's next -->
                                            <p style="margin:0 0 12px;color:#a1a1aa;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;">What you can do with Findly</p>
                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td style="padding:8px 0;">
                                                        <table cellpadding="0" cellspacing="0">
                                                            <tr>
                                                                <td style="width:32px;height:32px;background:rgba(37,99,235,0.1);border-radius:8px;text-align:center;vertical-align:middle;font-size:14px;">📦</td>
                                                                <td style="padding-left:12px;color:#a1a1aa;font-size:13px;line-height:1.5;">Report lost or found items instantly</td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding:8px 0;">
                                                        <table cellpadding="0" cellspacing="0">
                                                            <tr>
                                                                <td style="width:32px;height:32px;background:rgba(16,185,129,0.1);border-radius:8px;text-align:center;vertical-align:middle;font-size:14px;">🤖</td>
                                                                <td style="padding-left:12px;color:#a1a1aa;font-size:13px;line-height:1.5;">AI-powered matching to reunite items with owners</td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td style="padding:8px 0;">
                                                        <table cellpadding="0" cellspacing="0">
                                                            <tr>
                                                                <td style="width:32px;height:32px;background:rgba(139,92,246,0.1);border-radius:8px;text-align:center;vertical-align:middle;font-size:14px;">💬</td>
                                                                <td style="padding-left:12px;color:#a1a1aa;font-size:13px;line-height:1.5;">Chat securely with finders and owners</td>
                                                            </tr>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>

                                    <!-- Footer -->
                                    <tr>
                                        <td style="background:#0a0a0c;border-top:1px solid rgba(255,255,255,0.06);padding:24px 40px;text-align:center;">
                                            <p style="margin:0 0 6px;color:#3f3f46;font-size:12px;">
                                                This email was sent to <span style="color:#52525b;">{user.email}</span>
                                            </p>
                                            <p style="margin:0;color:#3f3f46;font-size:12px;">
                                                © 2026 Findly. All rights reserved.
                                            </p>
                                        </td>
                                    </tr>

                                </table>
                            </td>
                        </tr>
                    </table>
                </body>
                </html>
                """

                text_body = f"Welcome to Findly, {user.first_name or 'there'}!\n\nYour OTP is: {otp}\n\nThis code expires in 10 minutes. Do not share it with anyone.\n\n© 2026 Findly"

                msg = EmailMultiAlternatives(
                    subject="Verify your Findly account 🔐",
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                print(f"✅ OTP sent to {user.email}: {otp}")

            except Exception as e:
                print(f"❌ OTP email failed: {e}")


def verifyOtpView(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('core:signup')
    if request.method == "POST":
        otp_entered = request.POST.get('otp', '').strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('core:signup')
        if user.otp_created_at:
            expiry = user.otp_created_at + timezone.timedelta(minutes=10)
            if timezone.now() > expiry:
                messages.error(request, "OTP expired. Please sign up again.")
                user.delete()
                return redirect('core:signup')
            if otp_entered == user.otp_code:
                user.is_active = True
                user.otp_code = None
                user.otp_created_at = None
                user.save()
                if 'verify_email' in request.session:
                    del request.session['verify_email']

                # Auto login after verification
                login(request, user)
                messages.success(request, "✅ Email verified! Welcome to Findly.")

                if user.role == "Admin":
                    return redirect("found:admin_dashboard")
                elif user.role == "Owner":
                    return redirect("found:owner_dashboard")
                elif user.role == "Finder":
                    return redirect("found:finder_dashboard")
        else:
            messages.error(request, "Incorrect OTP. Please try again.")
            return render(request, 'core/verify_otp.html', {'email': email})
    return render(request, 'core/verify_otp.html', {'email': email})


def resendOtpView(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('core:signup')
    try:
        user = User.objects.get(email=email)
        otp = str(random.randint(100000, 999999))
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_mail(
            subject="Findly — New OTP",
            message=f"Your new Findly OTP is: {otp}\n\nExpires in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f"New OTP sent to {email}: {otp}")
        messages.success(request, "New OTP sent!")
    except Exception as e:
        messages.error(request, f"Failed to resend OTP: {e}")
    return redirect('core:verify_otp')


def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'core/login.html', {'form': form, 'error': "Invalid email or password"})
            if not user.check_password(password):
                return render(request, 'core/login.html', {'form': form, 'error': "Invalid email or password"})
            if not user.is_active:
                otp = str(random.randint(100000, 999999))
                user.otp_code = otp
                user.otp_created_at = timezone.now()
                user.save()
                try:
                    send_mail(
                        subject="Findly — Verify Your Email",
                        message=f"Your Findly OTP is: {otp}\n\nExpires in 10 minutes.",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    print(f"OTP resent to {user.email}: {otp}")
                except Exception as e:
                    print(f"OTP email failed: {e}")
                request.session['verify_email'] = user.email
                messages.error(request, "Your email is not verified. We sent a new OTP to your inbox.")
                return redirect('core:verify_otp')
            login(request, user)
            print(f"Logged in: {user.email} | Role: {user.role}")
            if user.role == "Admin":
                return redirect("found:admin_dashboard")
            elif user.role == "Owner":
                return redirect("found:owner_dashboard")
            elif user.role == "Finder":
                return redirect("found:finder_dashboard")
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('core:login')


def home_view(request):
    recent_lost  = Item.objects.filter(report_type='Lost',  status='Active').order_by('-created_at')[:6]
    recent_found = Item.objects.filter(report_type='Found', status='Active').order_by('-created_at')[:6]
    return render(request, 'core/homepage.html', {'recent_lost': recent_lost, 'recent_found': recent_found})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('core:profile')
    else:
        form = UserProfileForm(instance=request.user)
    reviews = Review.objects.filter(target_user=request.user).order_by('-created_at')
    return render(request, 'core/profile.html', {'form': form, 'reviews': reviews})


@login_required
def report_lost_view(request):
    form = ReportLostItemForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(reporter=request.user)
        run_matching_algorithm(item)
        messages.success(request, f"Lost item reported! ID: {item.item_id}")
        return redirect('core:item_detail', pk=item.item_id)
    return render(request, 'core/report_lost.html', {'form': form})


@login_required
def report_found_view(request):
    form = ReportFoundItemForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save(reporter=request.user)
        run_matching_algorithm(item)
        messages.success(request, "Found item reported!")
        return redirect('core:item_detail', pk=item.item_id)
    return render(request, 'core/report_found.html', {'form': form})


def item_detail_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'core/item_detail.html', {'item': item})


@login_required
def my_items_view(request):
    items = Item.objects.filter(reporter=request.user).order_by('-created_at')
    return render(request, 'core/my_items.html', {'items': items})


@login_required
def confirm_recovery_view(request, pk):
    item = get_object_or_404(Item, pk=pk, reporter=request.user)
    item.status = 'Recovered'
    item.save()
    messages.success(request, "Item marked as Recovered!")
    return redirect('core:my_items')


def search_items_view(request):
    form  = ItemSearchForm(request.GET or None)
    items = Item.objects.filter(status='Active')
    if form.is_valid():
        query       = form.cleaned_data.get('query')
        category    = form.cleaned_data.get('category')
        report_type = form.cleaned_data.get('report_type')
        lat         = form.cleaned_data.get('latitude')
        lng         = form.cleaned_data.get('longitude')
        radius_km   = form.cleaned_data.get('radius_km') or 10
        if query:
            items = items.filter(Q(description__icontains=query) | Q(category__icontains=query))
        if category:
            items = items.filter(category=category)
        if report_type:
            items = items.filter(report_type=report_type)
        if lat and lng:
            items = [i for i in items if _haversine(float(lat), float(lng), float(i.latitude), float(i.longitude)) <= radius_km]
    return render(request, 'core/search.html', {'form': form, 'items': items})


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    a = sin((lat2-lat1)/2)**2 + cos(lat1)*cos(lat2)*sin((lon2-lon1)/2)**2
    return R * 2 * asin(sqrt(a))


@login_required
def match_chat_view(request, match_id):
    match   = get_object_or_404(Match, pk=match_id)
    msgs    = match.messages.order_by('sent_at')
    form    = MessageForm(request.POST or None)
    allowed = [match.lost_item.reporter, match.found_item.reporter]
    if request.user not in allowed:
        messages.error(request, "You are not part of this match.")
        return redirect('core:home')
    if request.method == 'POST' and form.is_valid():
        msg        = form.save(commit=False)
        msg.match  = match
        msg.sender = request.user
        msg.save()
        other = allowed[1] if request.user == allowed[0] else allowed[0]
        send_notification(other, f"New message from {request.user.first_name or request.user.email}")
        return redirect('core:match_chat', match_id=match_id)
    return render(request, 'core/match_chat.html', {'match': match, 'messages': msgs, 'form': form})


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifs})


def notification_count_api(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})


@login_required
def submit_review_view(request, item_id, target_user_id):
    item        = get_object_or_404(Item, pk=item_id)
    target_user = get_object_or_404(User, pk=target_user_id)
    form        = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review             = form.save(commit=False)
        review.author      = request.user
        review.target_user = target_user
        review.item        = item
        review.save()
        messages.success(request, "Review submitted!")
        return redirect('core:home')
    return render(request, 'core/review.html', {'form': form, 'target_user': target_user, 'item': item})


def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def owner_dashboard(request):
    return render(request, 'owner_dashboard.html')

def finder_dashboard(request):
    return render(request, 'finder_dashboard.html')