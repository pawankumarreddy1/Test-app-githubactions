from rest_framework import serializers
from apps.hostelmanagement.models import Floor, Room, Bed, Student
 
class RoomSerializer(serializers.ModelSerializer):
    total_beds = serializers.SerializerMethodField()
    occupied_beds = serializers.SerializerMethodField()
    available_beds = serializers.SerializerMethodField()
 
    class Meta:
        model = Room
        fields = [
            'room_id', 'room_number', 'room_type', 'preference',
            'monthly_rent', 'total_beds', 'occupied_beds', 'available_beds'
        ]
 
    def get_total_beds(self, obj):
        return obj.beds.count()
 
    def get_occupied_beds(self, obj):
        return obj.beds.filter(is_occupied=True).count()
 
    def get_available_beds(self, obj):
        return obj.beds.filter(is_occupied=False).count()
 
 
class FloorSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True)
    total_rooms = serializers.SerializerMethodField()
 
    class Meta:
        model = Floor
        fields = ['floor_id', 'floor_number', 'total_rooms', 'rooms']
 
    def get_total_rooms(self, obj):
        # dynamically count rooms for this floor
        return obj.rooms.count()
 
 
class OccupiedBedSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    student_name = serializers.CharField(source='student.student_name', read_only=True)
 
    class Meta:
        model = Bed
        fields = ['bed_id', 'room_number', 'bed_number', 'student_name']
 
 
class StudentReportSerializer(serializers.ModelSerializer):
    bed_number = serializers.CharField(source='allocated_bed.bed_number', read_only=True)
    room_number = serializers.CharField(source='allocated_bed.room.room_number', read_only=True)
    floor_number = serializers.IntegerField(source='allocated_bed.room.floor.floor_number', read_only=True)
    building_name = serializers.CharField(source='allocated_bed.room.floor.building.building_name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'student_id', 'student_name', 'mobile_number', 'aadhar_number', 'address',
            'date_of_birth', 'emergency_name', 'emergency_phone',
            'bed_number', 'room_number', 'floor_number', 'building_name'
        ]


class TotalBedSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    floor_number = serializers.IntegerField(source='room.floor.floor_number', read_only=True)
    building_name = serializers.CharField(source='room.floor.building.building_name', read_only=True)
    building_id = serializers.UUIDField(source='room.floor.building.building_id', read_only=True)
    status = serializers.SerializerMethodField()
    monthly_rent = serializers.SerializerMethodField()

    class Meta:
        model = Bed
        fields = [
            'bed_id', 'bed_number', 'room_number', 'floor_number', 
            'building_name', 'building_id', 'status', 'monthly_rent', 'created_at'
        ]

    def get_status(self, obj):
        return "occupied" if obj.is_occupied else "available"

    def get_monthly_rent(self, obj):
        return obj.monthly_rent or obj.room.monthly_rent


class OccupiedBedDetailSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    floor_number = serializers.IntegerField(source='room.floor.floor_number', read_only=True)
    building_name = serializers.CharField(source='room.floor.building.building_name', read_only=True)
    building_id = serializers.UUIDField(source='room.floor.building.building_id', read_only=True)
    student_name = serializers.CharField(source='allocations.first.student.student_name', read_only=True)
    student_mobile = serializers.CharField(source='allocations.first.student.mobile_number', read_only=True)
    allocated_at = serializers.DateTimeField(source='allocations.first.allocated_at', read_only=True)
    monthly_rent = serializers.SerializerMethodField()

    class Meta:
        model = Bed
        fields = [
            'bed_id', 'bed_number', 'room_number', 'floor_number',
            'building_name', 'building_id', 'student_name', 'student_mobile',
            'allocated_at', 'monthly_rent', 'created_at'
        ]

    def get_monthly_rent(self, obj):
        return obj.monthly_rent or obj.room.monthly_rent
 