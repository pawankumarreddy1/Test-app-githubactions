from django.contrib import admin
from .models import CollectFee

@admin.register(CollectFee)
class CollectFeeAdmin(admin.ModelAdmin):
    # Fields to display in list view
    list_display = (
        "fee_id",
        "student",
        "payment_type",
        "amount",
        "payment_method",
        "transaction_reference",
        "payment_date",
    )

    # Fields you can filter by
    list_filter = (
        "payment_type",
        "payment_method",
        "payment_date",
    )

    # Fields that can be searched
    search_fields = (
        "student__student_name",
        "transaction_reference",
        "remarks",
    )

    # Fields that are read-only
    readonly_fields = (
        "fee_id",
        "updated_at",
    )

    # Optional: ordering
    ordering = ("-payment_date",)

    # Optional: show a date hierarchy
    date_hierarchy = "payment_date"
