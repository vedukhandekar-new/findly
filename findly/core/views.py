from django.shortcuts import render, redirect,HttpResponse
from .forms import UserSignupForm,UserLoginForm
from django.contrib.auth import authenticate,login
# Create your views here.
def userSignupView(request):
    if request.method =="POST":
      form = UserSignupForm(request.POST or None)
      if form.is_valid():
        form.save()
        return redirect('core:login') #error
      else:
        return render(request,'core/signup.html',{'form':form})  
    else:
        form = UserSignupForm()
        return render(request,'core/signup.html',{'form':form})
    

# def userLoginView(request):
#   if request.method =="POST":
#     form = UserLoginForm(request.POST )
#     if form.is_valid():
#       print(form.cleaned_data)
#       email = form.cleaned_data['email']
#       password = form.cleaned_data['password']
#       user = authenticate(request,email=email,password=password) #it will check in database..

#       print("USER OBJECT:", user)

#       if user:
#         login(request,user)
#         if user.role == "owner":
#           return redirect("owner_dashboard") #parking.urls.py name...
#         elif user.role == "finder":
#           return redirect("finder_dashboard") #parking.urls.py name...
#       else:
#         return render(request,'core/login.html',{'form':form})  
    
#   else:
#     form = UserLoginForm()
#     return render(request,'core/login.html',{'form':form})
  

# def userLoginView(request):
#     if request.method == "POST":
#         form = UserLoginForm(request.POST or None)

#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']

#             user = authenticate(request, email=email, password=password)

#             if user:
#                 login(request, user)

#                 if user.role == "owner":
#                     return redirect("owner_dashboard")

#                 elif user.role == "user":
#                     return redirect("user_dashboard")

#                 else:
#                     return redirect("core:login")  # fallback

#             else:
#                 return render(request, 'core/login.html', {
#                     'form': form,
#                     'error': "Invalid email or password"
#                 })

#         # ✅ IMPORTANT: If form is NOT valid
#         return render(request, 'core/login.html', {'form': form})

#     # ✅ GET request
#     form = UserLoginForm()
#     return render(request, 'core/login.html', {'form': form})


def userLoginView(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # ✅ FIX 1: use username instead of email
            user = authenticate(request, email=email, password=password)

            print("USER OBJECT:", user)

            if user is not None:
                login(request, user)

                if user.role == "owner":
                    return redirect("owner_dashboard")

                elif user.role == "finder":
                    return redirect("finder_dashboard")

                # ✅ fallback
                return redirect("core:login")

            else:
                return render(request, 'core/login.html', {
                    'form': form,
                    'error': "Invalid email or password"
                })

        # ✅ FIX 2: return if form invalid
        return render(request, 'core/login.html', {'form': form})

    # ✅ GET request
    form = UserLoginForm()
    return render(request, 'core/login.html', {'form': form})