from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Redirect root URL to login if user is not authenticated, else go to home
def redirect_to_login_or_home(request):
    if request.user.is_authenticated:
        return redirect("home")  # If logged in, go to home
    return redirect("login")  # Otherwise, go to login

urlpatterns = [
    path('', redirect_to_login_or_home, name='root_redirect'),  # Root URL redirects dynamically
    path('admin/', admin.site.urls),
    path('master/', include('master.urls')),  # Include your app URLs
     path('raw_material/', include('raw_material.urls')), 

]
