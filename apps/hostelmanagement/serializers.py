
from rest_framework import serializers
from django.db import models
from .models import Bed, Building, Floor, Hostel, Room, Inventory, RoomInventory, Student

class BedSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    floor_number = serializers.IntegerField(source='room.floor.floor_number', read_only=True)
    monthly_rent = serializers.SerializerMethodField()

    class Meta:
        model = Bed
        fields = [
            "bed_id",
            "status",
            "room_number",
            "floor_number",
            "bed_number",
            "is_occupied",
            "monthly_rent",
            "created_at",
        ]

    def get_status(self, obj):
        return "booked" if obj.is_occupied else "empty"

    def get_monthly_rent(self, obj):
        return obj.monthly_rent or obj.room.monthly_rent


class InventoryDetailSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ["inventory_id", "inventory_type", "quantity"]

    def get_quantity(self, obj):
        # Access the room passed via serializer context
        room = self.context.get("room")
        if not room:
            return None
        try:
            return RoomInventory.objects.get(room=room, inventory=obj).quantity
        except RoomInventory.DoesNotExist:
            return None





class RoomSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()
    floor_id = serializers.UUIDField(source='floor.floor_id', read_only=True)
    building_id = serializers.UUIDField(source='floor.building.building_id', read_only=True)
    hostel_id = serializers.UUIDField(source='floor.building.hostel.hostel_id', read_only=True)

    inventories = serializers.SerializerMethodField()  

    class Meta:
        model = Room
        fields = "__all__"

    def create(self, validated_data):
        room = Room.objects.create(**validated_data)
        return room

    def get_is_available(self, obj):
        return obj.beds.filter(is_occupied=False).exists()

    # ✅ You need this method for SerializerMethodField
    def get_inventories(self, obj):
        inventories = obj.inventories.all()
        return InventoryDetailSerializer(inventories, many=True, context={"room": obj}).data


class RoomInventoryItemSerializer(serializers.Serializer):
    inventory_type = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)


class BulkRoomUpdateItemSerializer(serializers.Serializer):
    room_id = serializers.UUIDField()
    room_number = serializers.CharField(required=False)
    room_type = serializers.CharField(required=False)
    preference = serializers.CharField(required=False)
    total_beds = serializers.CharField(required=False)
    monthly_rent = serializers.CharField(required=False)
    is_available = serializers.BooleanField(required=False)
    inventories = serializers.ListField(
        child=serializers.DictField(), required=False
    )

class BulkRoomUpdateSerializer(serializers.Serializer):
    rooms = BulkRoomUpdateItemSerializer(many=True)

    def validate_rooms(self, value):
        if not value:
            raise serializers.ValidationError("At least one room update is required.")
        return value

    def update(self, instance, validated_data):
        """
        Not used (bulk update has no instance), DRF calls save() → update() here manually.
        """
        pass

    def save(self, **kwargs):
        """
        Handle bulk update manually.
        """
        rooms_data = self.validated_data.get("rooms", [])
        updated_rooms = []
        not_found_ids = []

        for room_data in rooms_data:
            room_id = room_data.get("room_id")
            try:
                room = Room.objects.get(room_id=room_id)
            except Room.DoesNotExist:
                not_found_ids.append(str(room_id))
                continue

            # ✅ Update basic fields
            for field in ["room_number", "room_type", "preference", "total_beds", "monthly_rent", "is_available"]:
                if field in room_data:
                    setattr(room, field, room_data[field])
            room.save()

            # ✅ Handle inventories if provided
            inventories_data = room_data.get("inventories", [])
            if inventories_data:
                # Clear and recreate
                RoomInventory.objects.filter(room=room).delete()
                for inv in inventories_data:
                    inv_type = inv.get("inventory_type")
                    quantity = inv.get("quantity", 1)
                    inventory_obj, _ = Inventory.objects.get_or_create(inventory_type=inv_type)
                    RoomInventory.objects.create(room=room, inventory=inventory_obj, quantity=quantity)

            updated_rooms.append(room)

        return {"updated_rooms": updated_rooms, "not_found": not_found_ids}


class FloorSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True)
    class Meta:
        model = Floor
        fields = "__all__"


class BuildingSerializer(serializers.ModelSerializer):
    floors = FloorSerializer(many=True, read_only=True)
    class Meta:
        model = Building
        fields = "__all__"

class BuildingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["building_id", "building_name", "total_floors", "building_type", "created_at"]

# Hostel serializer showing only buildings
class HostelSerializer(serializers.ModelSerializer):
    buildings = BuildingDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Hostel
        fields = "__all__"

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = "__all__"


class RoomInventorySerializer(serializers.ModelSerializer):
    inventory_items = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ["room_id", "room_number", "inventory_items"]

    def get_inventory_items(self, obj):
        inventories = Inventory.objects.filter(room=obj)
        return [
            {
                "inventory_id": str(inv.inventory_id),
                "name": inv.inventory_type,
                "quantity": inv.quantity
            }
            for inv in inventories
        ]


class FloorTotalRoomsUpdateSerializer(serializers.Serializer):
    floor = serializers.UUIDField()
    total_rooms = serializers.IntegerField(min_value=0)
    
    def validate_floor(self, value):
        try:
            floor = Floor.objects.get(floor_id=value)
            return floor
        except Floor.DoesNotExist:
            raise serializers.ValidationError("Floor not found")


class BulkFloorTotalRoomsUpdateSerializer(serializers.Serializer):
    floors_data = FloorTotalRoomsUpdateSerializer(many=True)
    
    def validate_floors_data(self, value):
        if not value:
            raise serializers.ValidationError("At least one floor update is required")
        return value



class StudentSerializer(serializers.ModelSerializer):
    allocated_bed = BedSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            'student_id',
            'student_name',
            'mobile_number',
            'aadhar_number',
            'address',
            'aadhar_image',
            'date_of_birth',
            'emergency_name',
            'emergency_phone',
            'allocated_bed',
            'created_at',
            'updated_at',
        ]

from rest_framework import serializers
from .models import Student

class StudentSimpleSerializer(serializers.ModelSerializer):
    floor_number = serializers.IntegerField(source='allocated_bed.room.floor.floor_number', read_only=True)
    room_number = serializers.CharField(source='allocated_bed.room.room_number', read_only=True)
    bed_number = serializers.CharField(source='allocated_bed.bed_number', read_only=True)
    monthly_rent = serializers.SerializerMethodField()
    due_amount = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    last_payment = serializers.SerializerMethodField()
    payment_amount = serializers.SerializerMethodField()
    
    def get_monthly_rent(self, obj):
        """Get monthly rent from allocated bed"""
        if obj.allocated_bed and obj.allocated_bed.monthly_rent:
            try:
                return float(obj.allocated_bed.monthly_rent)
            except (ValueError, TypeError):
                return 0
        return 0
    
    def get_due_amount(self, obj):
        """Calculate due amount: monthly rent - last payment amount"""
        from apps.feemanagement.models import CollectFee
        
        monthly_rent = self.get_monthly_rent(obj)
        
        # Get the most recent Monthly_Rent payment amount
        last_payment = CollectFee.objects.filter(
            student=obj,
        ).order_by('-payment_date').first()
        
        # Get the last payment amount
        last_payment_amount = float(last_payment.amount) if last_payment else 0
        
        due = monthly_rent - last_payment_amount
        return max(due, 0) 
    
    def get_status(self, obj):
        """Return 'overdue' if due amount is present, else 'pending'"""
        due_amount = self.get_due_amount(obj)
        return 'overdue' if due_amount > 0 else 'paid'
    
    def get_last_payment(self, obj):
        """Get the date of the most recent Monthly_Rent payment from CollectFee"""
        from apps.feemanagement.models import CollectFee
        last_fee = CollectFee.objects.filter(
            student=obj,
        ).order_by('-payment_date').first()
        return last_fee.payment_date if last_fee else None
    
    def get_payment_amount(self, obj):
        """Get the amount of the most recent Monthly_Rent payment from CollectFee"""
        from apps.feemanagement.models import CollectFee
        last_fee = CollectFee.objects.filter(
            student=obj,
        ).order_by('-payment_date').first()
        return float(last_fee.amount) if last_fee else 0
    
    class Meta:
        model = Student
        fields = [
            'student_id',
            'student_name',
            'mobile_number',
            'floor_number',
            'room_number',
            'bed_number',
            'monthly_rent',
            'due_amount',
            'status',
            'last_payment',
            'payment_amount',
        ]

# --- inventory serielizer---
class RoomDetailInventorySerializer(serializers.ModelSerializer):
    inventory_type = serializers.CharField(source='inventory.inventory_type')

    class Meta:
        model = RoomInventory
        fields = ['inventory_type', 'quantity']

class RoomInventorySerializer(serializers.ModelSerializer):
    inventories = RoomDetailInventorySerializer(source='roominventory_set', many=True)

    class Meta:
        model = Room
        fields = ['room_id', 'room_number', 'room_type', 'inventories']

class FloorInventorySerializer(serializers.ModelSerializer):
    rooms = RoomInventorySerializer(many=True)  
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['rooms'] = [room for room in data['rooms'] if room['room_number']]
        return data
    class Meta:
        model = Floor
        fields = ['floor_id', 'floor_number', 'rooms']
class BuildingInventorySerializer(serializers.ModelSerializer):
    floors = FloorInventorySerializer(many=True)

    class Meta:
        model = Building
        fields = ['building_id', 'building_name', 'floors']
    
    def to_representation(self, instance):
        """Filter out floors that have no valid rooms."""
        data = super().to_representation(instance)
        data['floors'] = [floor for floor in data['floors'] if floor['rooms']]
        return data
    