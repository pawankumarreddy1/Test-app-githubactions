import uuid
from django.core.validators import RegexValidator
from django.db import models
from core.settings.cloudinary_storage import CloudinaryStorage
class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES, null=False, blank=False
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(r"^\+?\d{10,15}$", message="Enter a valid phone number")
        ],
        null=False,
        blank=False,
        unique=True,
    )
    email = models.EmailField(unique=True, null=False, blank=False)
    password = models.CharField(max_length=128, null=False, blank=False)
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("warden", "Warden"),
        ("worker", "Worker"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=False, blank=False) 
    expiry_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.email


class Subscription(models.Model):
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    ACCOUNT_TYPE_CHOICES = [
        ("free_trial", "Free Trial"),
        ("premium", "Premium"),
    ]
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    reciept = models.FileField(
        upload_to="reciepts/", 
        storage=CloudinaryStorage(),
        null=True, 
        blank=True
    )
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.subscription_id)

