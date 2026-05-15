from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from math import radians, cos, sin, asin, sqrt
import os
import random

import logging
from django.core.mail import send_mail
from .models import User

from .forms import (
    UserSignupForm, UserLoginForm, UserProfileForm,
    ReportLostItemForm, ReportFoundItemForm, ItemSearchForm,
    MessageForm, ReviewForm,
)
from .models import User, Item, Match, Message, Notification, Review, Payment
from .utils import run_matching_algorithm, send_notification
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────
# WELCOME EMAIL — sent on signup, no OTP
# ─────────────────────────────────────────

def send_welcome_email(user):
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Welcome to Findly!</title>
</head>
<body style="margin:0;padding:0;background-color:#09090B;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#09090B;padding:40px 20px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background-color:#121214;border-radius:20px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">

  <tr>
    <td style="background:linear-gradient(135deg,#1d4ed8,#4f46e5);padding:48px 40px;text-align:center;">
      <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 20px auto;">
        <tr>
          <td width="64" height="64" style="background:rgba(255,255,255,0.15);border-radius:18px;text-align:center;vertical-align:middle;">
            <span style="font-size:30px;line-height:64px;">&#128269;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0 0 8px 0;color:#ffffff;font-size:32px;font-weight:800;letter-spacing:-0.5px;">Findly</h1>
      <p style="margin:0;color:rgba(255,255,255,0.65);font-size:14px;">Lost &amp; Found Platform</p>
    </td>
  </tr>

  <tr>
    <td style="padding:0;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:linear-gradient(135deg,rgba(16,185,129,0.12),rgba(5,150,105,0.08));border-bottom:1px solid rgba(16,185,129,0.2);padding:20px 40px;text-align:center;">
            <p style="margin:0;color:#34d399;font-size:15px;font-weight:600;">&#127881; &nbsp;Thank you for joining Findly!</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="padding:40px 40px 32px 40px;">
      <h2 style="margin:0 0 12px 0;color:#f4f4f5;font-size:24px;font-weight:800;">Welcome aboard, {user.first_name or 'there'}! &#128075;</h2>
      <p style="margin:0 0 28px 0;color:#71717a;font-size:14px;line-height:1.8;">
        Thank you for registering with <strong style="color:#a1a1aa;">Findly</strong>. We are thrilled to have you as part of our community. Findly is built to make recovering lost items easier, faster, and more reliable &#8212; and you are now part of that mission.
      </p>

      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 28px 0;">

      <table cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr>
          <td style="background:rgba(37,99,235,0.1);border:1px solid rgba(59,130,246,0.3);border-radius:10px;padding:14px 20px;">
            <p style="margin:0 0 4px 0;color:#93c5fd;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;">Your Account</p>
            <p style="margin:0;color:#f4f4f5;font-size:15px;font-weight:600;">{user.email} &nbsp;&#183;&nbsp; <span style="color:#60a5fa;">{user.role}</span></p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 16px 0;color:#a1a1aa;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Get started in 3 steps</p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            <table cellpadding="0" cellspacing="0" width="100%"><tr>
              <td width="40" style="vertical-align:top;padding-top:2px;">
                <span style="display:inline-block;width:28px;height:28px;background:linear-gradient(135deg,#2563eb,#4f46e5);border-radius:8px;color:#fff;font-size:13px;font-weight:800;text-align:center;line-height:28px;">1</span>
              </td>
              <td style="padding-left:12px;">
                <p style="margin:0 0 3px 0;color:#e4e4e7;font-size:14px;font-weight:600;">Log in and verify your email</p>
                <p style="margin:0;color:#71717a;font-size:12px;line-height:1.6;">You will receive an OTP on your first login to verify your email</p>
              </td>
            </tr></table>
          </td>
        </tr>
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
            <table cellpadding="0" cellspacing="0" width="100%"><tr>
              <td width="40" style="vertical-align:top;padding-top:2px;">
                <span style="display:inline-block;width:28px;height:28px;background:linear-gradient(135deg,#2563eb,#4f46e5);border-radius:8px;color:#fff;font-size:13px;font-weight:800;text-align:center;line-height:28px;">2</span>
              </td>
              <td style="padding-left:12px;">
                <p style="margin:0 0 3px 0;color:#e4e4e7;font-size:14px;font-weight:600;">Report a lost or found item</p>
                <p style="margin:0;color:#71717a;font-size:12px;line-height:1.6;">Describe the item with details and location for best results</p>
              </td>
            </tr></table>
          </td>
        </tr>
        <tr>
          <td style="padding:12px 0;">
            <table cellpadding="0" cellspacing="0" width="100%"><tr>
              <td width="40" style="vertical-align:top;padding-top:2px;">
                <span style="display:inline-block;width:28px;height:28px;background:linear-gradient(135deg,#2563eb,#4f46e5);border-radius:8px;color:#fff;font-size:13px;font-weight:800;text-align:center;line-height:28px;">3</span>
              </td>
              <td style="padding-left:12px;">
                <p style="margin:0 0 3px 0;color:#e4e4e7;font-size:14px;font-weight:600;">Let AI do the matching</p>
                <p style="margin:0;color:#71717a;font-size:12px;line-height:1.6;">Our system notifies you when a potential match is found</p>
              </td>
            </tr></table>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="31%" style="text-align:center;padding:18px 10px;background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
            <p style="margin:0 0 6px 0;color:#f4f4f5;font-size:22px;font-weight:800;">AI</p>
            <p style="margin:0;color:#71717a;font-size:11px;line-height:1.4;">Powered<br>Matching</p>
          </td>
          <td width="3%"></td>
          <td width="31%" style="text-align:center;padding:18px 10px;background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
            <p style="margin:0 0 6px 0;color:#f4f4f5;font-size:22px;font-weight:800;">&#128272;</p>
            <p style="margin:0;color:#71717a;font-size:11px;line-height:1.4;">Secure<br>Chat</p>
          </td>
          <td width="3%"></td>
          <td width="31%" style="text-align:center;padding:18px 10px;background:rgba(255,255,255,0.02);border-radius:12px;border:1px solid rgba(255,255,255,0.06);">
            <p style="margin:0 0 6px 0;color:#f4f4f5;font-size:22px;font-weight:800;">&#11088;</p>
            <p style="margin:0;color:#71717a;font-size:11px;line-height:1.4;">Verified<br>Reviews</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="background:#0a0a0c;border-top:1px solid rgba(255,255,255,0.06);padding:24px 40px;text-align:center;">
      <p style="margin:0 0 4px 0;color:#3f3f46;font-size:12px;">This email was sent to <span style="color:#52525b;">{user.email}</span></p>
      <p style="margin:0;color:#3f3f46;font-size:12px;">&#169; 2026 Findly. All rights reserved.</p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    text_body = f"Welcome to Findly, {user.first_name or 'there'}!\n\nThank you for registering. Log in to verify your email and get started.\n\nRole: {user.role}\nEmail: {user.email}\n\n© 2026 Findly"
    try:
        msg = EmailMultiAlternatives(
            subject=f"Welcome to Findly, {user.first_name or 'there'}!",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        print(f"Welcome email sent to {user.email}")
    except Exception as e:
        print(f"Welcome email failed: {e}")


# ─────────────────────────────────────────
# OTP EMAIL — sent on first login
# ─────────────────────────────────────────

def send_otp_email(user, otp):
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Verify Your Email - Findly</title>
</head>
<body style="margin:0;padding:0;background-color:#09090B;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#09090B;padding:40px 20px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background-color:#121214;border-radius:20px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">

  <tr>
    <td style="background:linear-gradient(135deg,#1d4ed8,#4f46e5);padding:36px 40px;text-align:center;">
      <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px auto;">
        <tr>
          <td width="52" height="52" style="background:rgba(255,255,255,0.15);border-radius:14px;text-align:center;vertical-align:middle;">
            <span style="font-size:24px;line-height:52px;">&#128269;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:800;letter-spacing:-0.5px;">Findly</h1>
      <p style="margin:6px 0 0;color:rgba(255,255,255,0.65);font-size:13px;">Lost &amp; Found Platform</p>
    </td>
  </tr>

  <tr>
    <td style="padding:36px 40px;">
      <h2 style="margin:0 0 8px 0;color:#f4f4f5;font-size:20px;font-weight:700;">Verify your email, {user.first_name or 'there'} &#128274;</h2>
      <p style="margin:0 0 24px 0;color:#71717a;font-size:14px;line-height:1.7;">
        Use the OTP below to verify your Findly account. This code is valid for <strong style="color:#a1a1aa;">10 minutes</strong> only.
      </p>

      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 24px 0;">

      <p style="margin:0 0 12px 0;color:#a1a1aa;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Your Verification Code</p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
        <tr>
          <td style="background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(79,70,229,0.15));border:1px solid rgba(59,130,246,0.35);border-radius:14px;padding:28px 20px;text-align:center;">
            <p style="margin:0 0 8px 0;color:#93c5fd;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;">One-Time Password</p>
            <p style="margin:0;color:#ffffff;font-size:44px;font-weight:800;letter-spacing:14px;font-family:'Courier New',Courier,monospace;">{otp}</p>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr>
          <td style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.25);border-radius:10px;padding:12px 16px;">
            <p style="margin:0;color:#fbbf24;font-size:13px;">&#9200; This code expires in <strong>10 minutes</strong>. Do not share it with anyone.</p>
          </td>
        </tr>
      </table>

      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 24px 0;">

      <p style="margin:0 0 16px 0;color:#a1a1aa;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">What you can do with Findly</p>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="padding:8px 0;">
          <table cellpadding="0" cellspacing="0"><tr>
            <td width="36" height="36" style="background:rgba(37,99,235,0.12);border-radius:8px;text-align:center;vertical-align:middle;font-size:16px;">&#128230;</td>
            <td style="padding-left:12px;color:#a1a1aa;font-size:13px;line-height:1.6;">Report lost or found items instantly</td>
          </tr></table>
        </td></tr>
        <tr><td style="padding:8px 0;">
          <table cellpadding="0" cellspacing="0"><tr>
            <td width="36" height="36" style="background:rgba(16,185,129,0.12);border-radius:8px;text-align:center;vertical-align:middle;font-size:16px;">&#129302;</td>
            <td style="padding-left:12px;color:#a1a1aa;font-size:13px;line-height:1.6;">AI-powered matching to reunite items with owners</td>
          </tr></table>
        </td></tr>
        <tr><td style="padding:8px 0;">
          <table cellpadding="0" cellspacing="0"><tr>
            <td width="36" height="36" style="background:rgba(139,92,246,0.12);border-radius:8px;text-align:center;vertical-align:middle;font-size:16px;">&#128172;</td>
            <td style="padding-left:12px;color:#a1a1aa;font-size:13px;line-height:1.6;">Chat securely with finders and owners</td>
          </tr></table>
        </td></tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="background:#0a0a0c;border-top:1px solid rgba(255,255,255,0.06);padding:24px 40px;text-align:center;">
      <p style="margin:0 0 4px 0;color:#3f3f46;font-size:12px;">This email was sent to <span style="color:#52525b;">{user.email}</span></p>
      <p style="margin:0;color:#3f3f46;font-size:12px;">&#169; 2026 Findly. All rights reserved.</p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    text_body = f"Hi {user.first_name or 'there'},\n\nYour Findly OTP is: {otp}\n\nExpires in 10 minutes. Do not share it.\n\n© 2026 Findly"
    try:
        msg = EmailMultiAlternatives(
            subject="Verify your Findly email",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        print(f"OTP email sent to {user.email}: {otp}")
    except Exception as e:
        print(f"OTP email failed: {e}")


# ─────────────────────────────────────────
# SIGNUP — save user, send welcome email,
#          redirect to LOGIN (not verify)
# ─────────────────────────────────────────

# def userSignupView(request):

#     # Redirect if already logged in
#     if request.user.is_authenticated:
#         if request.user.role == "Admin":
#             return redirect("found:admin_dashboard")
#         else:
#             return redirect("found:user_dashboard")


#     if request.method == "POST":
#         form = UserSignupForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False  # inactive until OTP verified on login
#             user.save()
#             send_welcome_email(user)
#             messages.success(request, f"Account created! Please log in to verify your email.")
#             return redirect('core:login')
#         else:
#             print("SIGNUP ERRORS:", form.errors)
#             return render(request, 'core/signup.html', {'form': form})
#     else:
#         form = UserSignupForm()
#         return render(request, 'core/signup.html', {'form': form})
def userSignupView(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False 
                
                otp = str(random.randint(100000, 999999))
                user.otp_code = otp
                user.save()
                
                try:
                    send_mail(
                        'Your Findly OTP',
                        f'Your verification code is: {otp}',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    request.session['verify_email'] = user.email
                    messages.success(request, "OTP sent to your email!")
                    return redirect('core:verify_otp')
                
                except Exception as email_err:
                    logger.error(f"Email Failed: {email_err}")
                    user.delete()
                    messages.error(request, f"Email error: {str(email_err)}")
                    # FIX: Match the path used at the bottom
                    return render(request, 'core/signup.html', {'form': form})

            except Exception as db_err:
                logger.error(f"Database Error: {db_err}")
                messages.error(request, "A database error occurred.")
                # FIX: Match the path used at the bottom
                return render(request, 'core/signup.html', {'form': form})
        else:
            messages.error(request, "Invalid form data.")
    else:
        form = UserSignupForm()
    
    # This is your "Main" return
    return render(request, 'core/signup.html', {'form': form})
# ─────────────────────────────────────────
# LOGIN — if inactive, send OTP and
#         redirect to verify page
# ─────────────────────────────────────────

def userLoginView(request):
    
    # Redirect if already logged in
    if request.user.is_authenticated:
        if request.user.role == "Admin":
            return redirect("found:admin_dashboard")
        else:
            return redirect("found:user_dashboard")

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
                # Send OTP for email verification
                otp = str(random.randint(100000, 999999))
                user.otp_code = otp
                user.otp_created_at = timezone.now()
                user.save()
                send_otp_email(user, otp)
                request.session['verify_email'] = user.email
                messages.success(request, f"OTP sent to {user.email}. Please verify your email.")
                return redirect('core:verify_otp')
            # Already verified — log in directly
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            print(f"Logged in: {user.email} | Role: {user.role}")
            if user.role == "Admin":
                return redirect("found:admin_dashboard")
            else:
                return redirect("found:user_dashboard")
    else:
        form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})


# ─────────────────────────────────────────
# VERIFY OTP
# ─────────────────────────────────────────

# def verifyOtpView(request):
#     email = request.session.get('verify_email')
#     if not email:
#         return redirect('core:login')
#     if request.method == "POST":
#         otp_entered = request.POST.get('otp', '').strip()
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             messages.error(request, "User not found.")
#             return redirect('core:login')
#         if user.otp_created_at:
#             expiry = user.otp_created_at + timezone.timedelta(minutes=10)
#             if timezone.now() > expiry:
#                 messages.error(request, "OTP expired. Please log in again.")
#                 return redirect('core:login')
#         if otp_entered == user.otp_code:
#             user.is_active = True
#             user.otp_code = None
#             user.otp_created_at = None
#             user.save()
#             if 'verify_email' in request.session:
#                 del request.session['verify_email']
#             login(request, user)
#             messages.success(request, "Email verified! Welcome to Findly.")
#             if user.role == "Admin":
#                 return redirect("found:admin_dashboard")
#             else:
#                 return redirect("found:user_dashboard")
#         else:
#             messages.error(request, "Incorrect OTP. Please try again.")
#             return render(request, 'core/verify_otp.html', {'email': email})
#     return render(request, 'core/verify_otp.html', {'email': email})
def verify_otp(request):
    email = request.session.get('verify_email')

    if not email:
        messages.error(request, 'Session expired or invalid access. Please sign up again.')
        return redirect('core:signup')

    if request.method == 'POST':
        user_entered_otp = request.POST.get('otp')

        try:
            user = User.objects.get(email=email)

            # FIX 1: Add OTP expiry check — was completely missing before
            if user.otp_created_at:
                expiry = user.otp_created_at + timezone.timedelta(minutes=10)
                if timezone.now() > expiry:
                    messages.error(request, 'OTP has expired. Please sign up again.')
                    user.delete()
                    del request.session['verify_email']
                    return redirect('core:signup')

            if user.otp_code == user_entered_otp:
                user.is_active = True
                user.otp_code = None
                user.otp_created_at = None
                user.save()

                del request.session['verify_email']

                # FIX 2: Specify backend — without this login() crashes
                # with "ValueError: must have exactly one backend"
                login(request, user,
                      backend='django.contrib.auth.backends.ModelBackend')

                messages.success(request, 'Account verified successfully! Welcome to Findly.')

                # FIX 3: Redirect based on role, not just to login
                if user.role == 'Admin':
                    return redirect('found:admin_dashboard')
                else:
                    return redirect('found:user_dashboard')

            else:
                messages.error(request, 'Invalid OTP. Please check your email and try again.')

        except User.DoesNotExist:
            messages.error(request, 'Critical Error: User record not found.')
            return redirect('core:signup')

    return render(request, 'core/verify_otp.html', {'email': email})

# ─────────────────────────────────────────
# RESEND OTP
# ─────────────────────────────────────────

def resendOtpView(request):
    email = request.session.get('verify_email')
    if not email:
        return redirect('core:login')
    try:
        user = User.objects.get(email=email)
        otp = str(random.randint(100000, 999999))
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()
        send_otp_email(user, otp)
        messages.success(request, "New OTP sent to your email!")
    except Exception as e:
        messages.error(request, f"Failed to resend OTP: {e}")
    return redirect('core:verify_otp')


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────

def user_logout(request):
    logout(request)
    return redirect('core:login')


# ─────────────────────────────────────────
# HOME
# ─────────────────────────────────────────

def home_view(request):
    recent_lost  = Item.objects.filter(report_type='Lost',  status='Active').order_by('-created_at')[:6]
    recent_found = Item.objects.filter(report_type='Found', status='Active').order_by('-created_at')[:6]
    total_users     = User.objects.filter(is_active=True).count()
    total_recovered = Item.objects.filter(status='Recovered').count()
    return render(request, 'core/homepage.html', {
        'recent_lost'    : recent_lost,
        'recent_found'   : recent_found,
        'total_users'    : total_users,
        'total_recovered': total_recovered,
    })


# ─────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# ITEM VIEWS
# ─────────────────────────────────────────

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
    # Hide blocked items from non-admin users
    if item.is_blocked and (not request.user.is_authenticated or request.user.role != 'Admin'):
        return render(request, 'core/item_blocked.html', {'item': item})
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


# ─────────────────────────────────────────
# SEARCH
# ─────────────────────────────────────────

def search_items_view(request):
    form  = ItemSearchForm(request.GET or None)
    items = Item.objects.filter(status='Active', is_blocked=False)
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


# ─────────────────────────────────────────
# MESSAGING
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# REVIEW
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# PAYMENT EMAIL
# ─────────────────────────────────────────

def send_payment_email(match, payment):
    user   = match.found_item.reporter
    owner  = match.lost_item.reporter
    amount = payment.amount
    txn_id = payment.transaction_id

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Reward Received - Findly</title>
</head>
<body style="margin:0;padding:0;background-color:#09090B;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#09090B;padding:40px 20px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background-color:#121214;border-radius:20px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">

  <tr>
    <td style="background:linear-gradient(135deg,#059669,#10b981);padding:40px;text-align:center;">
      <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px auto;">
        <tr>
          <td width="60" height="60" style="background:rgba(255,255,255,0.15);border-radius:16px;text-align:center;vertical-align:middle;">
            <span style="font-size:28px;line-height:60px;">&#128176;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0 0 8px 0;color:#ffffff;font-size:28px;font-weight:800;">Reward Received!</h1>
      <p style="margin:0;color:rgba(255,255,255,0.75);font-size:14px;">Payment confirmed on Findly</p>
    </td>
  </tr>

  <tr>
    <td style="padding:36px 40px;">
      <h2 style="margin:0 0 12px 0;color:#f4f4f5;font-size:20px;font-weight:700;">Hello, {user.first_name or 'there'} &#128075;</h2>
      <p style="margin:0 0 24px 0;color:#71717a;font-size:14px;line-height:1.8;">
        Great news! You have received a reward payment from <strong style="color:#a1a1aa;">{owner.first_name or 'the owner'} {owner.last_name or ''}</strong> for returning their lost item. Thank you for being an honest member of the Findly community!
      </p>

      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 24px 0;">

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
        <tr>
          <td style="background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(5,150,105,0.15));border:1px solid rgba(16,185,129,0.3);border-radius:14px;padding:28px 20px;text-align:center;">
            <p style="margin:0 0 8px 0;color:#6ee7b7;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;">Reward Amount</p>
            <p style="margin:0;color:#ffffff;font-size:44px;font-weight:800;font-family:'Courier New',monospace;">&#8377;{amount}</p>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
        <tr>
          <td style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px 20px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr><td style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                <span style="color:#71717a;font-size:12px;">Transaction ID</span>
                <span style="color:#f4f4f5;font-size:12px;font-weight:600;float:right;font-family:monospace;">{txn_id}</span>
              </td></tr>
              <tr><td style="padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
                <span style="color:#71717a;font-size:12px;">Paid By</span>
                <span style="color:#f4f4f5;font-size:12px;font-weight:600;float:right;">{owner.first_name or ''} {owner.last_name or ''}</span>
              </td></tr>
              <tr><td style="padding:6px 0;">
                <span style="color:#71717a;font-size:12px;">Item Returned</span>
                <span style="color:#f4f4f5;font-size:12px;font-weight:600;float:right;">{match.lost_item.category}</span>
              </td></tr>
            </table>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:linear-gradient(135deg,rgba(37,99,235,0.1),rgba(79,70,229,0.1));border:1px solid rgba(59,130,246,0.2);border-radius:12px;padding:20px;text-align:center;">
            <p style="margin:0 0 8px 0;font-size:24px;">&#127775;</p>
            <p style="margin:0 0 4px 0;color:#e4e4e7;font-size:14px;font-weight:700;">Good Samaritan Award</p>
            <p style="margin:0;color:#71717a;font-size:13px;">Keep returning items to build your reputation on Findly!</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="background:#0a0a0c;border-top:1px solid rgba(255,255,255,0.06);padding:24px 40px;text-align:center;">
      <p style="margin:0 0 4px 0;color:#3f3f46;font-size:12px;">This email was sent to <span style="color:#52525b;">{user.email}</span></p>
      <p style="margin:0;color:#3f3f46;font-size:12px;">&#169; 2026 Findly. All rights reserved.</p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    text_body = f"Hello {user.first_name or 'there'},\n\nYou received a reward of ₹{amount}!\nTransaction ID: {txn_id}\nPaid by: {owner.first_name or 'the owner'}\n\n© 2026 Findly"
    try:
        msg = EmailMultiAlternatives(
            subject=f"💰 You received ₹{amount} reward on Findly!",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        print(f"Payment email sent to finder: {user.email}")
    except Exception as e:
        print(f"Payment email failed: {e}")


# ─────────────────────────────────────────
# PAYMENT VIEWS
# ─────────────────────────────────────────

# @login_required
# def payment_view(request, match_id):
#     match = get_object_or_404(Match, pk=match_id)

#     # Only owner of the lost item can pay
#     if request.user != match.lost_item.reporter:
#         messages.error(request, "Only the item owner can make this payment.")
#         return redirect('found:user_dashboard')

#     # Redirect if no reward set
#     if not match.lost_item.reward_amount or match.lost_item.reward_amount <= 0:
#         messages.error(request, "No reward amount set for this item.")
#         return redirect('found:user_dashboard')

#     # Redirect if already paid
#     try:
#         if match.payment.status == 'Completed':
#             messages.info(request, "Reward already paid for this match.")
#             return redirect('core:payment_success', match_id=match_id)
#     except Payment.DoesNotExist:
#         pass

#     finder = match.found_item.reporter
#     return render(request, 'core/payment.html', {
#         'match'  : match,
#         'amount' : match.lost_item.reward_amount,
#         'finder' : finder,
#     })


@login_required
def process_payment_view(request, match_id):
    if request.method != 'POST':
        return redirect('core:payment', match_id=match_id)

    match  = get_object_or_404(Match, pk=match_id)

    # Security check
    if request.user != match.lost_item.reporter:
        messages.error(request, "Unauthorized payment attempt.")
        return redirect('found:user_dashboard')

    amount = match.lost_item.reward_amount

    # Generate transaction ID
    import string
    transaction_id = 'FDL_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    # Create or update payment record
    payment, created = Payment.objects.get_or_create(
        match    = match,
        defaults = {
            'payer'          : request.user,
            'receiver'       : match.found_item.reporter,
            'amount'         : amount,
            'status'         : 'Completed',
            'transaction_id' : transaction_id,
        }
    )
    if not created:
        payment.status         = 'Completed'
        payment.transaction_id = transaction_id
        payment.save()

    # In-app notification to finder
    send_notification(
        match.found_item.reporter,
        f"💰 You received a reward of ₹{amount} from {request.user.first_name or request.user.email} for returning the {match.lost_item.category}!"
    )

    # Send payment email to finder
    send_payment_email(match, payment)

    messages.success(request, f"✅ Reward of ₹{amount} successfully sent to {match.found_item.reporter.first_name or 'the finder'}!")
    return redirect('core:payment_success', match_id=match_id)


@login_required
def payment_success_view(request, match_id):
    match   = get_object_or_404(Match, pk=match_id)
    payment = get_object_or_404(Payment, match=match)

    # Only owner or finder can see this
    allowed = [match.lost_item.reporter, match.found_item.reporter]
    if request.user not in allowed:
        return redirect('core:home')

    return render(request, 'core/payment_success.html', {
        'match'  : match,
        'payment': payment,
        'finder' : match.found_item.reporter,
    })

@login_required
def flag_item_view(request, pk):
    item = get_object_or_404(Item, pk=pk)
    reasons = [
        ('Dangerous weapon or harmful item', 'Dangerous weapon or harmful item'),
        ('Hazardous material or substance',  'Hazardous material or substance'),
        ('Stolen item',                      'Stolen item'),
        ('Fake or misleading report',        'Fake or misleading report'),
        ('Inappropriate content',            'Inappropriate content'),
        ('Other suspicious activity',        'Other suspicious activity'),
    ]

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if request.user in item.flagged_by.all():
            messages.warning(request, "You have already flagged this item.")
            return redirect('core:item_detail', pk=pk)
        item.flagged_by.add(request.user)
        item.flag_count += 1
        if item.flag_count >= 3:
            item.status = 'UnderReview'
        item.save()
        admins = User.objects.filter(role='Admin')
        for admin in admins:
            send_notification(
                admin,
                f"🚨 Item flagged: {item.category} | Reason: {reason} | Flags: {item.flag_count}"
            )
        messages.success(request, "✅ Item reported. Thank you for keeping Findly safe!")
        return redirect('core:item_detail', pk=pk)

    return render(request, 'core/flag_item.html', {'item': item, 'reasons': reasons})


# ─────────────────────────────────────────
# PLACEHOLDER DASHBOARD VIEWS
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# FORGOT PASSWORD
# ─────────────────────────────────────────

def forgotPasswordView(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            otp  = str(random.randint(100000, 999999))
            user.otp_code       = otp
            user.otp_created_at = timezone.now()
            user.save()
            send_otp_email(user, otp)
            request.session['reset_email'] = user.email
            messages.success(request, f"OTP sent to {user.email}. Check your inbox.")
            return redirect('core:forgot_otp')
        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")
    return render(request, 'core/forgot_password.html')


def forgotOtpView(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('core:forgot_password')
    if request.method == "POST":
        otp_entered = request.POST.get('otp', '').strip()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('core:forgot_password')
        if user.otp_created_at:
            expiry = user.otp_created_at + timezone.timedelta(minutes=10)
            if timezone.now() > expiry:
                messages.error(request, "OTP expired. Please try again.")
                return redirect('core:forgot_password')
        if otp_entered == user.otp_code:
            user.otp_code       = None
            user.otp_created_at = None
            user.save()
            request.session['reset_verified'] = True
            return redirect('core:reset_password')
        else:
            messages.error(request, "Incorrect OTP. Please try again.")
    return render(request, 'core/forgot_otp.html', {'email': email})


def resetPasswordView(request):
    email    = request.session.get('reset_email')
    verified = request.session.get('reset_verified')
    if not email or not verified:
        return redirect('core:forgot_password')
    if request.method == "POST":
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.")
        else:
            try:
                user = User.objects.get(email=email)
                user.set_password(password1)
                user.save()
                del request.session['reset_email']
                del request.session['reset_verified']
                messages.success(request, "Password reset successfully! Please log in.")
                return redirect('core:login')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
    return render(request, 'core/reset_password.html', {'email': email})


# ─────────────────────────────────────────
# PLACEHOLDER DASHBOARD VIEWS
# ─────────────────────────────────────────

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


def custom_404(request, exception=None):
    
    return render(request, '404.html', status=404)