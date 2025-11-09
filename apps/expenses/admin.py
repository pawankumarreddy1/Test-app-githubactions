from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("expense_uuid", "date", "nature_of_expense", "amount")
    list_filter = ("date", "nature_of_expense")
    search_fields = ("expense_uuid", "nature_of_expense")
    ordering = ("-date",)
    readonly_fields = ("expense_uuid",)

    fieldsets = (
        ("Expense Details", {
            "fields": ("expense_uuid", "date", "nature_of_expense", "amount")
        }),
    )
