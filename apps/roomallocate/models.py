import uuid
from django.db import models
from apps.hostelinfo.models import User
from apps.hostelmanagement.models import Bed, Building, Floor, Hostel, Room

class RoomAllocation(models.Model):
    allocation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="allocations")
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name="allocations")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="allocations")
    allocated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="allocated_students",
    )
    allocated_at = models.DateTimeField(auto_now_add=True)

    def _refresh_room_availability(self, room):
        # Count occupied beds from Bed rows (defensive) and derive available using total_beds
        occupied_beds = Bed.objects.filter(room=room, is_occupied=True).count()
        total = room.total_beds or 0
        available_beds = max(0, total - occupied_beds)
        room.is_available = available_beds > 0
        room.save(update_fields=["is_available"])

    def save(self, *args, **kwargs):
        # Mark the bed as occupied (persist first so counts reflect DB)
        if not self.bed.is_occupied:
            self.bed.is_occupied = True
            self.bed.save(update_fields=["is_occupied"])
        super().save(*args, **kwargs)
        # Update room availability using total_beds (authoritative)
        self._refresh_room_availability(self.room)

    def delete(self, *args, **kwargs):
        # Keep references before deletion
        room = self.room
        bed = self.bed

        # Free the bed
        if bed.is_occupied:
            bed.is_occupied = False
            bed.save(update_fields=["is_occupied"])

        super().delete(*args, **kwargs)
        # Update room availability after allocation removed
        self._refresh_room_availability(room)

    def __str__(self):
        return f"Allocation {str(self.allocation_id)} for {self.student.full_name}"

class StudentRoomIssues(models.Model):
    ISSUE_CHOICES = [
        ("water", "Water Problem"),
        ("electricity", "Electricity Issue"),
        ("cleaning", "Cleaning Issue"),
        ("wifi", "Wi-Fi Issue"),
        ("furniture", "Furniture Damage"),
        ("other", "Other"),
    ]
    RESOLUTION_STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("solved", "Solved"),
        ("not_solved", "Not Solved"),
    ]
    issue_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="room_issues")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_issues")
    issue_type = models.CharField(max_length=50, choices=ISSUE_CHOICES)
    issue_description = models.TextField(blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    resolution_status = models.CharField(
        max_length=20, choices=RESOLUTION_STATUS_CHOICES, default="in_progress"
    )
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Issue {str(self.issue_id)} by {self.student.full_name} - Status: {self.resolution_status}"