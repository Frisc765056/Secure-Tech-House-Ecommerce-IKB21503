from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# --- B.1: SECURITY REQUIREMENT - REGEX WHITELISTING (OWASP ASVS V5) ---
# Prevents script injection or special character attacks.
alphanumeric = RegexValidator(r'^[a-zA-Z0-9 ]*$', 'Only alphanumeric characters and spaces are allowed.')

# --- B.2: SECURITY REQUIREMENT - ACCOUNT-SPECIFIC LOCKOUT (OWASP ASVS V2) ---
# Tracks failed attempts per user/IP to prevent global DoS lockouts.
class LoginAttempt(models.Model):
    username = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    failed_attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} - {self.failed_attempts} attempts"

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('RAM', 'RAM'),
        ('GPU', 'Graphics Card'),
        ('CPU', 'CPU'),
        ('HDD', 'Hard Disk'),
    ]
    
    name = models.CharField(max_length=200, validators=[alphanumeric])
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    description = models.TextField()
    
    # Prevents negative value injection.
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)]
    )
    stock = models.IntegerField(validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"

# --- B.8: SECURITY REQUIREMENT - AUDIT LOGGING (OWASP ASVS V7) ---
class AuditLog(models.Model):
    # SET_NULL ensures logs remain even if a user is deleted.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(null=True, blank=True) 
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{self.timestamp} - {username} - {self.action}"

# --- SIGNALS: AUTOMATED ADMIN ACTIVITY LOGGING (Requirement B.8) ---


# Captures creations and modifications in Django Admin while preventing duplicates.
@receiver(post_save, sender=User)
@receiver(post_save, sender=Product)
def log_admin_save(sender, instance, created, **kwargs):
    # Prevents duplicate logging during database initialization or complex saves.
    if kwargs.get('raw'):
        return

    action_str = f"ADMIN ACTION: New {sender.__name__} Created" if created else f"ADMIN ACTION: {sender.__name__} Modified"
    detail_str = f"Identifier: {instance} (ID: {instance.id})"
    AuditLog.objects.create(action=action_str, details=detail_str)

# Captures deletions in Django Admin.
@receiver(post_delete, sender=User)
@receiver(post_delete, sender=Product)
def log_admin_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        action=f"ADMIN ACTION: {sender.__name__} Deleted",
        details=f"Object: {instance} was permanently removed."
    )