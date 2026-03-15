from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from core.models import Item, Match, Notification, Review, User


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
def adminResolveMatchView(request, match_id, action):
    """Admin can verify or reject a match."""
    if request.user.role != 'Admin':
        return redirect('core:home')

    match = get_object_or_404(Match, pk=match_id)

    if action == 'verify':
        match.match_status          = 'Verified'
        match.lost_item.status      = 'Recovered'
        match.found_item.status     = 'Recovered'
        match.lost_item.save()
        match.found_item.save()
        messages.success(request, "Match verified and items marked as Recovered.")

    elif action == 'reject':
        match.match_status          = 'False'
        match.lost_item.status      = 'Active'
        match.found_item.status     = 'Active'
        match.lost_item.save()
        match.found_item.save()
        messages.warning(request, "Match rejected. Items set back to Active.")

    match.save()
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
