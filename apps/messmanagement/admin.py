from django.contrib import admin
from .models import Mess, Meal

class MealInline(admin.TabularInline):
    model = Meal
    extra = 1
    fields = ('meal', 'timing', 'status', 'menu')
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


@admin.register(Mess)
class MessAdmin(admin.ModelAdmin):
    list_display = ('building_id',)
    search_fields = ('building_id',)
    inlines = [MealInline]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('meal', 'mess', 'timing', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'meal')
    search_fields = ('meal', 'mess__building_id')
    ordering = ('mess', 'meal')
    readonly_fields = ('created_at', 'updated_at')
