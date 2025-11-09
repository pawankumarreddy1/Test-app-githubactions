from django.contrib import admin

from apps.hostelinfo.models import Subscription, User


# ------------------ User ------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "phone",
        "role",
        "gender",
        "created_at",
        "updated_at",
    )
    list_filter = ("role", "gender", "created_at")
    search_fields = ("full_name", "email", "phone")
    ordering = ("-created_at",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "account_type",
        "start_date",
        "end_date",
        "reciept",
        "created_at",
    )
    list_filter = ("account_type", "created_at")
    search_fields = ("user__full_name", "user__email", "user__phone")
    ordering = ("-created_at",)