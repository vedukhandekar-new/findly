from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from core.models import Item, Match, Notification, Review, User
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q


def send_recovery_email_owner(match):
    user   = match.lost_item.reporter
    item   = match.lost_item
    finder = match.found_item.reporter

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#09090B;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#09090B;padding:40px 20px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background-color:#121214;border-radius:20px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">

  <tr>
    <td style="background:linear-gradient(135deg,#059669,#10b981);padding:40px;text-align:center;">
      <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px auto;">
        <tr>
          <td width="60" height="60" style="background:rgba(255,255,255,0.15);border-radius:16px;text-align:center;vertical-align:middle;">
            <span style="font-size:28px;line-height:60px;">&#127881;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0 0 8px 0;color:#ffffff;font-size:28px;font-weight:800;">Item Recovered!</h1>
      <p style="margin:0;color:rgba(255,255,255,0.75);font-size:14px;">Great news from Findly</p>
    </td>
  </tr>

  <tr>
    <td style="padding:36px 40px;">
      <h2 style="margin:0 0 12px 0;color:#f4f4f5;font-size:20px;font-weight:700;">Hello, {user.first_name or 'there'} &#128075;</h2>
      <p style="margin:0 0 24px 0;color:#71717a;font-size:14px;line-height:1.8;">
        Your lost <strong style="color:#a1a1aa;">{item.category}</strong> has been successfully recovered and verified by our team. A big thank you to the finder for their honesty!
      </p>

      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 24px 0;">

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
        <tr>
          <td style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:12px;padding:16px 20px;">
            <p style="margin:0 0 4px 0;color:#6ee7b7;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Recovered Item</p>
            <p style="margin:0 0 6px 0;color:#f4f4f5;font-size:16px;font-weight:700;">{item.category}</p>
            <p style="margin:0;color:#71717a;font-size:13px;">{(item.description or '')[:80]}...</p>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
        <tr>
          <td style="background:rgba(37,99,235,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:12px;padding:16px 20px;">
            <p style="margin:0 0 4px 0;color:#93c5fd;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Found By</p>
            <p style="margin:0;color:#f4f4f5;font-size:15px;font-weight:600;">{finder.first_name or 'A Findly User'} {finder.last_name or ''}</p>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:10px;padding:14px 16px;">
            <p style="margin:0;color:#fbbf24;font-size:13px;">&#11088; Please leave a review for the finder to appreciate their effort!</p>
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

    text_body = f"Hello {user.first_name or 'there'},\n\nYour lost {item.category} has been recovered!\nFound by: {finder.first_name or 'A Findly User'}\n\n© 2026 Findly"
    try:
        msg = EmailMultiAlternatives(
            subject=f"🎉 Your lost {item.category} has been recovered!",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        print(f"Recovery email sent to owner: {user.email}")
    except Exception as e:
        print(f"Recovery email failed: {e}")


def send_recovery_email_finder(match):
    user  = match.found_item.reporter
    item  = match.found_item
    owner = match.lost_item.reporter

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background-color:#09090B;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#09090B;padding:40px 20px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;background-color:#121214;border-radius:20px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">

  <tr>
    <td style="background:linear-gradient(135deg,#2563eb,#4f46e5);padding:40px;text-align:center;">
      <table cellpadding="0" cellspacing="0" align="center" style="margin:0 auto 16px auto;">
        <tr>
          <td width="60" height="60" style="background:rgba(255,255,255,0.15);border-radius:16px;text-align:center;vertical-align:middle;">
            <span style="font-size:28px;line-height:60px;">&#127942;</span>
          </td>
        </tr>
      </table>
      <h1 style="margin:0 0 8px 0;color:#ffffff;font-size:28px;font-weight:800;">Thank You, Hero!</h1>
      <p style="margin:0;color:rgba(255,255,255,0.75);font-size:14px;">You made someone's day better</p>
    </td>
  </tr>

  <tr>
    <td style="padding:36px 40px;">
      <h2 style="margin:0 0 12px 0;color:#f4f4f5;font-size:20px;font-weight:700;">Hello, {user.first_name or 'there'} &#127775;</h2>
      <p style="margin:0 0 24px 0;color:#71717a;font-size:14px;line-height:1.8;">
        We want to personally thank you for returning the <strong style="color:#a1a1aa;">{item.category}</strong> to its rightful owner. Your honesty made a real difference!
      </p>

      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 24px 0;">

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
        <tr>
          <td style="background:rgba(37,99,235,0.08);border:1px solid rgba(59,130,246,0.2);border-radius:12px;padding:16px 20px;">
            <p style="margin:0 0 4px 0;color:#93c5fd;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">Item Returned</p>
            <p style="margin:0 0 4px 0;color:#f4f4f5;font-size:15px;font-weight:600;">{item.category}</p>
            <p style="margin:0;color:#71717a;font-size:13px;">Returned to: {owner.first_name or 'the owner'} {owner.last_name or ''}</p>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="background:linear-gradient(135deg,rgba(37,99,235,0.1),rgba(79,70,229,0.1));border:1px solid rgba(59,130,246,0.2);border-radius:12px;padding:20px;text-align:center;">
            <p style="margin:0 0 8px 0;font-size:24px;">&#127775;</p>
            <p style="margin:0 0 4px 0;color:#e4e4e7;font-size:15px;font-weight:700;">Good Samaritan Award</p>
            <p style="margin:0;color:#71717a;font-size:13px;">Your rating has been updated. Keep returning items to build your reputation!</p>
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

    text_body = f"Hello {user.first_name or 'there'},\n\nThank you for returning the {item.category}!\nYou are a true Good Samaritan.\n\n© 2026 Findly"
    try:
        msg = EmailMultiAlternatives(
            subject=f"🏆 Thank you for returning the {item.category}!",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        print(f"Recovery email sent to finder: {user.email}")
    except Exception as e:
        print(f"Recovery email failed: {e}")



# ─────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────

@login_required
def adminDashboardView(request):
    if request.user.role != 'Admin':
        return redirect('core:home')

    total_users     = User.objects.count()
    active_items    = Item.objects.filter(status='Active').count()
    recovered_items = Item.objects.filter(status='Recovered').count()
    pending_matches = Match.objects.filter(match_status='Pending').count()
    recent_items    = Item.objects.order_by('-created_at')[:10]
    all_matches     = Match.objects.select_related('lost_item', 'found_item').order_by('-created_at')[:10]

    context = {
        'total_users':     total_users,
        'active_items':    active_items,
        'recovered_items': recovered_items,
        'pending_matches': pending_matches,
        'recent_items':    recent_items,
        'all_matches':     all_matches,
    }
    return render(request, 'found/admin_dashboard.html', context)

@login_required
def blockItemView(request, pk):
    if request.user.role != 'Admin':
        return redirect('core:home')

    item = get_object_or_404(Item, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Blocked by Admin')
        item.is_blocked     = True
        item.status         = 'Blocked'
        item.blocked_reason = reason
        item.blocked_by     = request.user
        item.blocked_at     = timezone.now()
        item.save()

        # Notify item reporter
        from core.utils import send_notification
        send_notification(
            item.reporter,
            f"⚠️ Your reported {item.category} has been restricted by Admin. Reason: {reason}"
        )

        messages.success(request, f"✅ Item blocked successfully.")
        return redirect('found:flagged_items')

    return render(request, 'found/block_item.html', {'item': item})


@login_required
def unblockItemView(request, pk):
    if request.user.role != 'Admin':
        return redirect('core:home')

    item = get_object_or_404(Item, pk=pk)
    item.is_blocked     = False
    item.status         = 'Active'
    item.blocked_reason = None
    item.blocked_by     = None
    item.blocked_at     = None
    item.save()

    send_notification(
        item.reporter,
        f"✅ Your reported {item.category} has been reviewed and is now active again."
    )

    messages.success(request, "Item unblocked and set back to Active.")
    return redirect('found:flagged_items')


@login_required
def flaggedItemsView(request):
    if request.user.role != 'Admin':
        return redirect('core:home')

    flagged_items = Item.objects.filter(
        flag_count__gt=0
    ).order_by('-flag_count', '-created_at')

    blocked_items = Item.objects.filter(
        is_blocked=True
    ).order_by('-blocked_at')

    under_review = Item.objects.filter(
        status='UnderReview'
    ).order_by('-created_at')

    return render(request, 'found/flagged_items.html', {
        'flagged_items' : flagged_items,
        'blocked_items' : blocked_items,
        'under_review'  : under_review,
    })

@login_required
def adminResolveMatchView(request, match_id, action):
    if request.user.role != 'Admin':
        return redirect('core:home')

    match = get_object_or_404(Match, pk=match_id)

    if action == 'verify':
        match.match_status      = 'Verified'
        match.lost_item.status  = 'Recovered'
        match.found_item.status = 'Recovered'
        match.lost_item.save()
        match.found_item.save()
        match.save()

        # In-app notifications
        from core.utils import send_notification
        send_notification(
            match.lost_item.reporter,
            f"🎉 Your lost {match.lost_item.category} has been recovered! Thank you for using Findly."
        )
        send_notification(
            match.found_item.reporter,
            f"🏆 Thank you for returning the {match.found_item.category}! You are a true Good Samaritan."
        )

        # Recovery emails
        send_recovery_email_owner(match)
        send_recovery_email_finder(match)

        messages.success(request, "✅ Match verified! Both users have been notified.")

    elif action == 'reject':
        match.match_status      = 'False'
        match.lost_item.status  = 'Active'
        match.found_item.status = 'Active'
        match.lost_item.save()
        match.found_item.save()
        match.save()
        messages.warning(request, "Match rejected. Items set back to Active.")

    return redirect('found:admin_dashboard')


# ─────────────────────────────────────────
# OWNER DASHBOARD
# ─────────────────────────────────────────

@login_required
def ownerDashboardView(request):
    if request.user.role != 'Owner':
        return redirect('core:home')

    my_lost_items = Item.objects.filter(
        reporter=request.user, report_type='Lost'
    ).order_by('-created_at')

    # Matches where THIS user's lost item was matched
    my_matches = Match.objects.filter(
        lost_item__reporter=request.user
    ).select_related('found_item', 'found_item__reporter').order_by('-created_at')

    notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'my_lost_items': my_lost_items,
        'my_matches':    my_matches,
        'notifications': notifications,
    }
    return render(request, 'found/owner_dashboard.html', context)


# ─────────────────────────────────────────
# FINDER DASHBOARD
# ─────────────────────────────────────────

@login_required
def finderDashboardView(request):
    if request.user.role != 'Finder':
        return redirect('core:home')

    my_found_items = Item.objects.filter(
        reporter=request.user, report_type='Found'
    ).order_by('-created_at')

    # Matches where THIS user's found item was matched
    my_matches = Match.objects.filter(
        found_item__reporter=request.user
    ).select_related('lost_item', 'lost_item__reporter').order_by('-created_at')

    notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).order_by('-created_at')[:5]

    context = {
        'my_found_items': my_found_items,
        'my_matches':     my_matches,
        'notifications':  notifications,
    }
    return render(request, 'found/finder_dashboard.html', context)


# ─────────────────────────────────────────
# REVIEW MATCH  (your original route — now complete)
# ─────────────────────────────────────────

@login_required
def reviewMatchView(request):
    """Shows all pending matches for admin to review."""
    if request.user.role != 'Admin':
        return redirect('core:home')

    pending_matches = Match.objects.filter(
        match_status='Pending'
    ).select_related(
        'lost_item', 'lost_item__reporter',
        'found_item', 'found_item__reporter'
    ).order_by('-created_at')

    return render(request, 'found/review_match.html', {'pending_matches': pending_matches})

# ─────────────────────────────────────────
# MANAGE USERS
# ─────────────────────────────────────────

@login_required
def manageUsersView(request):
    if request.user.role != 'Admin':
        return redirect('core:home')

    # Get search query and role filter
    search = request.GET.get('search', '').strip()
    role   = request.GET.get('role', '')

    users = User.objects.all().order_by('-created_at')

    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)  |
            Q(email__icontains=search)
        )
    if role:
        users = users.filter(role=role)

    # Annotate each user with item counts
    from django.db.models import Count
    users = users.annotate(
        total_items=Count('reported_items', distinct=True),
        recovered_items=Count(
            'reported_items',
            filter=Q(reported_items__status='Recovered'),
            distinct=True
        )
    )

    # Handle activate/deactivate
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action  = request.POST.get('action')
        try:
            target_user = User.objects.get(pk=user_id)
            if target_user == request.user:
                messages.error(request, "You cannot deactivate your own account!")
            elif action == 'deactivate':
                target_user.is_active = False
                target_user.save()
                messages.success(request, f"✅ {target_user.email} has been deactivated.")
            elif action == 'activate':
                target_user.is_active = True
                target_user.save()
                messages.success(request, f"✅ {target_user.email} has been activated.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
        return redirect('found:manage_users')

    return render(request, 'found/manage_users.html', {
        'users':       users,
        'search':      search,
        'role_filter': role,
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
    })