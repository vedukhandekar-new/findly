from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required(login_url="login") #check in core.urls.py login name should exist..
def ownerDashboardView(request):
    return render(request,"found/owner_dashboard.html")

@login_required(login_url="login")
def finderDashboardView(request):
    return render(request,"found/finder_dashboard.html")