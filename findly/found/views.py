from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .decorators import role_required

# Create your views here.

# @login_required(login_url="login")
@role_required(allowed_roles=["Admin"])
def adminDashboardView(request):
    return render(request, "found/admin_dashboard.html")


# @login_required(login_url="login") #check in core.urls.py login name should exist..
@role_required(allowed_roles=["Owner"])
def ownerDashboardView(request):
    return render(request,"found/owner_dashboard.html")

# @login_required(login_url="login")
@role_required(allowed_roles=["Finder"])
def finderDashboardView(request):
    return render(request,"found/finder_dashboard.html")