from django.contrib import admin
from .models import RoomAllocation, StudentRoomIssues

@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ("allocation_id", "student", "allocated_by", "allocated_at")
    class Meta:
        model = RoomAllocation
        fields = "__all__"

@admin.register(StudentRoomIssues)
class StudentRoomIssuesAdmin(admin.ModelAdmin):
    list_display = ("issue_id", "student", "resolution_status",  "updated_at")
    class Meta:
        model = StudentRoomIssues
        fields = "__all__"