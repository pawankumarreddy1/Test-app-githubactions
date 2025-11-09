import uuid
from django.db import models

from apps.hostelmanagement.models import Building

class Expense(models.Model):
    expense_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="expenses",null=True, blank=True)
    date = models.DateField()
    nature_of_expense = models.CharField(max_length=255)
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.nature_of_expense} - {self.amount}"
