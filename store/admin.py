from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.templatetags.static import static
from .models import Product, AuditLog

# --- SAFE UNREGISTRATION ---
models_to_reset = [Product, AuditLog, User]
for model in models_to_reset:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass

# --- 1. PRODUCT ADMIN ---
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action_type = "Updated" if change else "Created"
        AuditLog.objects.create(
            user=request.user,
            action=f"ADMIN ACTION: Product {action_type}",
            details=f"Hardware: {obj.name}",
            ip_address=request.META.get('REMOTE_ADDR')
        )

    def delete_model(self, request, obj):
        AuditLog.objects.create(
            user=request.user,
            action="ADMIN ACTION: Product Deleted",
            details=f"Permanently removed hardware: {obj.name}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        super().delete_model(request, obj)

    class Media:
        css = {'all': (static('store/css/admin_custom.css') + '?v=1.2',)}

# --- 2. USER ADMIN ---
class UserAdmin(BaseUserAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:
            AuditLog.objects.create(
                user=request.user,
                action=f"ADMIN ACTION: User Permissions Modified",
                details=f"Updated status for {obj.username}. Staff: {obj.is_staff}",
                ip_address=request.META.get('REMOTE_ADDR')
            )

    def delete_model(self, request, obj):
        AuditLog.objects.create(
            user=request.user,
            action="ADMIN ACTION: User Deleted",
            details=f"Deleted account: {obj.username}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        super().delete_model(request, obj)

# --- 3. ENHANCED AUDIT LOG ADMIN (Self-Auditing Deletions) ---
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'ip_address', 'details')

    # Log SINGLE Log Deletions
    def delete_model(self, request, obj):
        AuditLog.objects.create(
            user=request.user,
            action="CRITICAL: Audit Log Entry Deleted",
            details=f"Admin deleted log ID {obj.id}: '{obj.action}' originally by {obj.user}",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        super().delete_model(request, obj)

    # Log BULK Log Deletions (Action dropdown)
    def delete_queryset(self, request, queryset):
        count = queryset.count()
        AuditLog.objects.create(
            user=request.user,
            action="CRITICAL: Bulk Audit Log Deletion",
            details=f"Admin deleted {count} security logs permanently.",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        queryset.delete()

    class Media:
        css = {'all': (static('store/css/admin_custom.css') + '?v=1.2',)}

# --- 4. REGISTRATION ---
admin.site.register(Product, ProductAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(AuditLog, AuditLogAdmin)