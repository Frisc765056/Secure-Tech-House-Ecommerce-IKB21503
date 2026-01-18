from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.password_validation import validate_password 
from django.core.exceptions import ValidationError, SuspiciousOperation 
from django.contrib import messages
from django.db import transaction 
from django.db.models import Q 
# Added LoginAttempt to imports for account-specific lockout [cite: 98]
from .models import Product, AuditLog, LoginAttempt 
from .forms import SearchForm 

# --- LOGIN VIEW (Requirement B.2: Account-Specific Lockout) ---
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        ip = request.META.get('REMOTE_ADDR')
        
        # Get or create tracking record for this specific user + IP (Prevents Global DoS) [cite: 98]
        attempt, _ = LoginAttempt.objects.get_or_create(username=username, ip_address=ip)

        # Verify if account is locked (5 failed attempts) [cite: 98, 99]
        if attempt.failed_attempts >= 5:
            AuditLog.objects.create(
                action=f"LOCKOUT TRIGGERED: {username}", 
                details=f"Account locked at 5 failed attempts from IP: {ip}",
                ip_address=ip
            )
            return render(request, 'registration/login.html', {
                'is_locked': True,
                'error_locked': f"SECURITY LOCKOUT: Account '{username}' is locked. Please contact admin."
            })

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Reset attempts on success [cite: 98]
            attempt.failed_attempts = 0
            attempt.save()
            
            user = form.get_user()
            login(request, user)
            
            AuditLog.objects.create(
                user=user,
                action="LOGIN SUCCESSFUL",
                ip_address=ip
            )
            return redirect('product_list')
        else: 
            # Increment failed attempts for this specific account [cite: 98]
            attempt.failed_attempts += 1
            attempt.save()
            
            AuditLog.objects.create(
                action=f"FAILED LOGIN ATTEMPT: {username}", 
                details=f"Failed attempt {attempt.failed_attempts} for this account.",
                ip_address=ip
            )
            
            messages.error(request, f"Invalid login. Attempt {attempt.failed_attempts} of 5.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form, 'is_locked': False})

# --- REGISTRATION VIEW (OWASP: Strong Password Enforcement) ---
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        raw_p = request.POST.get('password1') or request.POST.get('password')

        if form.is_valid():
            try:
                if raw_p:
                    validate_password(raw_p) # Enforce strong password rules [cite: 99]
            except ValidationError as e:
                for error in e.messages:
                    form.add_error(None, error) 
                return render(request, 'registration/register.html', {'form': form})

            user = form.save()
            
            AuditLog.objects.create(
                user=user, 
                action=f"ACCOUNT CREATED: {user.username}", 
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            login(request, user)
            return redirect('product_list')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

# --- SHOP & CART VIEWS ---
@login_required 
def product_list(request):
    form = SearchForm(request.GET or None)
    products = Product.objects.all()

    if request.GET:
        if form.is_valid():
            # Use of ORM prevents SQL Injection 
            query = form.cleaned_data['query']
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query)
            )
        else:
            # Log suspicious XSS/SQLi attempt blocked by regex 
            bad_query = request.GET.get('query', 'Unknown')
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action="SUSPICIOUS ACTIVITY: Blocked XSS/Injection Attempt",
                details=f"Query blocked by regex: {bad_query}",
                ip_address=request.META.get('REMOTE_ADDR')
            )

    return render(request, 'store/product_list.html', {
        'products': products, 
        'search_form': form
    })

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        subtotal = product.price * qty
        total += subtotal
        cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    
    AuditLog.objects.create(
        user=request.user,
        action=f"CART UPDATE: Increased quantity for {product.name}",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

@login_required
def decrease_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        product = get_object_or_404(Product, id=product_id)
        if cart[pid] > 1: 
            cart[pid] -= 1
            action_msg = f"REDUCED QUANTITY: {product.name}"
        else: 
            del cart[pid]
            action_msg = f"REMOVED FROM CART: {product.name}"
        
        AuditLog.objects.create(
            user=request.user,
            action=action_msg,
            ip_address=request.META.get('REMOTE_ADDR')
        )

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        product = get_object_or_404(Product, id=product_id)
        del cart[pid]
        
        AuditLog.objects.create(
            user=request.user,
            action=f"PERMANENTLY REMOVED FROM CART: {product.name}",
            ip_address=request.META.get('REMOTE_ADDR')
        )

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart_detail')

@login_required
@transaction.atomic
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart: 
        return redirect('product_list')
    
    item_list = []
    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        if product.stock >= qty:
            product.stock -= qty
            product.save()
            item_list.append(f"{product.name} (x{qty})")
        else:
            messages.error(request, f"Low stock: {product.name}")
            return redirect('cart_detail')
            
    AuditLog.objects.create(
        user=request.user,
        action="TRANSACTION: Checkout Complete",
        details=f"Purchased: {', '.join(item_list)}",
        ip_address=request.META.get('REMOTE_ADDR')
    )

    request.session['cart'] = {}
    return render(request, 'store/checkout_success.html')

# --- AUDIT & ERROR VIEWS ---

@login_required
def audit_log_view(request):
    # --- REQUIREMENT B.8: Log Unauthorized Access Attempts [cite: 125, 127] ---
    if not request.user.is_staff:
        # Record unauthorized access attempt before redirecting [cite: 104, 125]
        AuditLog.objects.create(
            user=request.user,
            action="ACCESS DENIED: Unauthorized Audit Log Access Attempt",
            details=f"Non-staff user '{request.user.username}' tried to view security logs.",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.error(request, "Security Alert: Administrative access required.")
        return redirect('login')

    logs = AuditLog.objects.all().order_by('-timestamp')
    return render(request, 'store/audit_log.html', {'logs': logs})

# --- USER PROFILE VIEW (Requirement A.4) [cite: 90] ---
@login_required
def profile_view(request):
    AuditLog.objects.create(
        user=request.user,
        action="VIEW PROFILE",
        details=f"User {request.user.username} viewed their profile settings.",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    return render(request, 'registration/profile.html', {'user': request.user})

# --- CUSTOM ERROR HANDLERS  ---
def custom_404(request, exception): 
    path_attempted = request.path
    
    # Ignore administrative false positives in logs 
    if not path_attempted.strip('/').startswith('admin'):
        user_involved = request.user if request.user.is_authenticated else None
        AuditLog.objects.create(
            user=user_involved,
            action=f"CLIENT ERROR: 404 Not Found - Tried to access '{path_attempted}'",
            ip_address=request.META.get('REMOTE_ADDR')
        )
    return render(request, 'errors/404.html', status=404)

def custom_403(request, exception=None, reason=None):
    user_involved = request.user if request.user.is_authenticated else None
    log_reason = reason if reason else "CSRF Verification Failed or Forbidden Access"
    AuditLog.objects.create(
        user=user_involved,
        action=f"SECURITY ALERT: 403 Forbidden - {log_reason}",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    return render(request, 'errors/403.html', status=403)

def custom_400(request, exception=None):
    AuditLog.objects.create(
        action="CLIENT ERROR: 400 Bad Request - Suspicious Operation",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    return render(request, 'errors/400.html', status=400)

def custom_500(request):
    AuditLog.objects.create(
        action="SERVER ERROR: 500 Internal System Failure",
        ip_address=request.META.get('REMOTE_ADDR')
    )
    return render(request, 'errors/500.html', status=500)