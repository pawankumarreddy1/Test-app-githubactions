import uuid
from django.db import models, transaction
from apps.hostelmanagement.models import Student

# Create your models here.

class CollectFee(models.Model):
    fee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
    PAYMENT_TYPE_CHOICES = [
      ("Deposit_Only", "Deposit Only"),
      ("Advance_Only", "Advance Only"),
      ("Deposit_Advance", "Deposit + Advance"),
      ("Monthly_Rent", "Monthly Rent"),
    ]
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    amount = models.IntegerField()
    STATUS_CHOICES = [
      ("cash", "Cash"),
      ("upi", "UPI"),
      ("bank", "Bank"),
      ("card", "Card"),
    ]
    payment_method = models.CharField(max_length=20, choices=STATUS_CHOICES)
    transaction_reference = models.CharField(max_length=255, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.fee_id)