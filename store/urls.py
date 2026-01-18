from django.urls import path
from . import views

urlpatterns = [
    # 1. Home page - Displays the product gallery
    path('', views.product_list, name='product_list'),
    
    # 2. Registration page - Secure account creation
    path('register/', views.register, name='register'),

    # 3. Product Detail - Dynamic path using Primary Key (pk)
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # 4. Audit Log - Restricted to Staff/Admins (Requirement A.5)
    path('audit-log/', views.audit_log_view, name='audit_log'),

    # 5. User Profile Page (Requirement A.4)
    # This maps to the secure profile_view in views.py
    path('profile/', views.profile_view, name='profile'),

    # 6. Shopping Cart Logic
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrease-cart/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # 7. Checkout
    path('checkout/', views.checkout, name='checkout'),
]