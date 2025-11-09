from django.contrib import admin
from .models import Bed, Building, Floor, Hostel, Room, Inventory, Student


# ------------------ Hostel ------------------
@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = (
        "hostel_name",
        "owner",
        "created_at",
    )

# ------------------ Building ------------------
@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = (
        "building_name",
        "hostel",
        "total_floors",
        "building_address",
        "building_type",
        "created_at",
    )

# ------------------ Floor ------------------
@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = (
        "floor_number",
        "building",
        "total_rooms",
        "created_at",
    )

# ------------------ Room ------------------
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = (
        "room_number",
        "get_building",
        "get_floor_number",
        "monthly_rent",
        "room_type",
        "is_available",
        "created_at",
    )

    def get_building(self, obj):
        return obj.floor.building.building_name

    get_building.short_description = "Building"

    def get_floor_number(self, obj):
        return obj.floor.floor_number

    get_floor_number.short_description = "Floor Number"

# ------------------ Bed ------------------
@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("bed_number", "get_room_number", "monthly_rent","is_occupied", "created_at")
    
    def get_room_number(self, obj):
        return obj.room.room_number

    get_room_number.short_description = "Room Number"


# ------------------ Inventory ------------------
@admin.register(Inventory) 
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("inventory_id", "inventory_type", "created_at")
    class Meta:
        model = Inventory
        fields = "__all__"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "student_name",
        "mobile_number",
        "aadhar_number",
        "get_bed_number",
        "get_room_number",
        "get_floor_number",
        "get_building_name",
        "get_hostel_name",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ("student_name", "mobile_number", "aadhar_number", "allocated_bed__bed_number")
    ordering = ("-created_at",)

    # === Custom Display Methods ===
    def get_bed_number(self, obj):
        return obj.allocated_bed.bed_number if obj.allocated_bed else "-"
    get_bed_number.short_description = "Bed Number"

    def get_room_number(self, obj):
        try:
            return obj.allocated_bed.room.room_number
        except AttributeError:
            return "-"
    get_room_number.short_description = "Room Number"

    def get_floor_number(self, obj):
        try:
            return obj.allocated_bed.room.floor.floor_number
        except AttributeError:
            return "-"
    get_floor_number.short_description = "Floor"

    def get_building_name(self, obj):
        try:
            return obj.allocated_bed.room.floor.building.building_name
        except AttributeError:
            return "-"
    get_building_name.short_description = "Building"

    def get_hostel_name(self, obj):
        try:
            return obj.allocated_bed.room.floor.building.hostel.hostel_name
        except AttributeError:
            return "-"
    get_hostel_name.short_description = "Hostel"