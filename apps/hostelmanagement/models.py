import uuid
from django.db import models

from apps.hostelinfo.models import User



# ------------------ Hostel Model ------------------
class Hostel(models.Model):
    hostel_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hostels")
    hostel_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.hostel_name


# ------------------ Building Model ------------------
class Building(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="buildings")
    building_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    building_name = models.CharField(max_length=200)
    building_address = models.TextField(null=True, blank=True)
    total_floors = models.IntegerField()
    BUILDING_TYPE_CHOICES = [
        ("boys", "Boys"),
        ("girls", "Girls"),
        ("coliving", "coliving"),
    ]
    building_type = models.CharField(max_length=10, choices=BUILDING_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.building_name




# ------------------ Floor Model ------------------
class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="floors")
    floor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    floor_number = models.IntegerField()
    total_rooms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.building.building_name} - Floor {self.floor_number}"



class Inventory(models.Model):
    inventory_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    INVENTORY_CHOICES = [
        ("fan", "Fan"),
        ("ac", "AC"),
        ("geyser", "Geyser"),
        ("tv", "TV"),
        ("light", "Light"),
    ]
    inventory_type = models.CharField(max_length=20, choices=INVENTORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.inventory_type

# ------------------ Room Model ------------------
class Room(models.Model):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, related_name="rooms")
    room_number = models.CharField(max_length=20, null=True, blank=True)

    ROOM_TYPE_CHOICES = [
        ("AC", "AC"),
        ("NON_AC", "NON_AC"),
    ]
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, null=True, blank=True)

    PREFERENCE_TYPE = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    preference = models.CharField(max_length=10, choices=PREFERENCE_TYPE, null=True, blank=True)

    total_beds = models.CharField(max_length=20, null=True, blank=True)
    monthly_rent = models.CharField(max_length=20, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    inventories = models.ManyToManyField(Inventory, through="RoomInventory", related_name="rooms")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Room {self.room_number} ({self.room_type})"

class RoomInventory(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('room', 'inventory')

    def __str__(self):
        return f"{self.room} - {self.inventory} ({self.quantity})"

# ------------------ Bed Model ------------------
class Bed(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="beds")
    bed_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bed_number = models.CharField(max_length=10)
    is_occupied = models.BooleanField(default=False)
    monthly_rent = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bed {self.bed_number} - Room {self.room.room_number}" if self.room else str(self.bed_id)

    


class Student(models.Model):
    student_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    student_name = models.CharField(max_length=50, null=True, blank=True)
    mobile_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    aadhar_number = models.CharField(max_length=12, null=True, blank=True, unique=True)
    address = models.TextField(null=True, blank=True)
    aadhar_image = models.FileField(upload_to="aadhar/", null=True, blank=True)
    allocated_bed = models.ForeignKey(Bed, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_name = models.CharField(max_length=50, null=True, blank=True)
    emergency_phone = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.student_name or "Unnamed Student"

