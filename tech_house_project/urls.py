from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve 
from store import views  # <--- CRITICAL IMPORT: We need this to access custom_login

urlpatterns = [
    # 1. Django Admin
    path('admin/', admin.site.urls),

    # --- SECURITY FIX: Force use of Custom Secure Login ---
    # We define these BEFORE 'django.contrib.auth.urls' so they take priority.
    # This ensures your Lockout Logic (Requirement B.2) is actually executed.
    path('login/', views.custom_login, name='login'),
    path('accounts/login/', views.custom_login), 

    # 2. Authentication (Logout/Password Reset)
    # We still include this for logout and password reset features
    path('accounts/', include('django.contrib.auth.urls')),

    # 3. Your Store App
    path('', include('store.urls')),
]

# THE SECURE STATIC HANDLER
# Force Django to serve static files from STATIC_ROOT when DEBUG is False
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    ]

# CUSTOM ERROR HANDLERS (Security Hardening for IKB 21503)
# These only trigger when DEBUG = False
handler404 = 'store.views.custom_404'
handler403 = 'store.views.custom_403'
handler400 = 'store.views.custom_400'
handler500 = 'store.views.custom_500' # <--- NEW HANDLER ADDED