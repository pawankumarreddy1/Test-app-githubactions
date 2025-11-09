from rest_framework import serializers
from .models import RoomAllocation, StudentRoomIssues
from apps.hostelmanagement.models import Bed
from apps.hostelinfo.models import User

class RoomAllocationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)
    hostel_name = serializers.CharField(source="hostel.hostel_name", read_only=True)
    building_name = serializers.CharField(source="building.building_name", read_only=True)
    floor_number = serializers.IntegerField(source="floor.floor_number", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True)
    room_type = serializers.CharField(source="room.room_type", read_only=True)
    bed_number = serializers.CharField(source="bed.bed_number", read_only=True)
    allocated_by_name = serializers.CharField(source="allocated_by.full_name", read_only=True)
    monthly_rent = serializers.IntegerField(source="room.monthly_rent", read_only=True)

    class Meta:
        model = RoomAllocation
        fields = [
            "allocation_id",
            "student",
            "student_name",
            "student_email",
            "bed",
            "bed_number",
            "room",
            "room_number",
            "room_type",
            "monthly_rent",
            "floor",
            "floor_number",
            "building",
            "building_name",
            "hostel",
            "hostel_name",
            "allocated_by",
            "allocated_by_name",
            "allocated_at",
        ]
        read_only_fields = [
            "allocation_id",
            "allocated_at",
            "hostel",
            "building",
            "floor",
            "room",
        ]

    def validate_bed(self, value):
        """Validate that the bed is not already occupied"""
        if value.is_occupied:
            raise serializers.ValidationError("This bed is already occupied.")
        return value

    def validate_student(self, value):
        """Validate that the student doesn't already have an allocation"""
        if RoomAllocation.objects.filter(student=value).exists():
            existing_allocation = RoomAllocation.objects.get(student=value)
            raise serializers.ValidationError(f"Student is already allocated to bed {existing_allocation.bed.bed_number} " f"in room {existing_allocation.room.room_number}")
        return value

    def validate(self, data):
        """Cross-field validation"""
        bed = data.get("bed")
        student = data.get("student")

        if bed and student:
            if bed.is_occupied:
                raise serializers.ValidationError("Selected bed is already occupied.")

            if RoomAllocation.objects.filter(student=student).exists():
                raise serializers.ValidationError("Student already has a room allocation.")

        return data



class AllocateBedSerializer(serializers.Serializer):
    bed_id = serializers.UUIDField()
    student_id = serializers.UUIDField()

    def validate(self, data):
        try:
            bed = Bed.objects.get(bed_id=data["bed_id"])
        except Bed.DoesNotExist:
            raise serializers.ValidationError({"bed_id": "Invalid Bed ID"})

        try:
            student = User.objects.get(user_id=data["student_id"], role="student")
        except User.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Invalid Student ID"})

        data["bed"] = bed
        data["student"] = student
        return data


class QuickAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAllocation
        fields = ["bed", "student"]

    def validate_bed(self, value):
        if value.is_occupied:
            raise serializers.ValidationError("This bed is already occupied.")
        return value

    def validate_student(self, value):
        if RoomAllocation.objects.filter(student=value).exists():
            raise serializers.ValidationError("Student already has an allocation.")
        return value


class AllocationSummarySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    room_info = serializers.SerializerMethodField()
    class Meta:
        model = RoomAllocation
        fields = ["allocation_id", "student_name", "room_info", "allocated_at"]

    def get_room_info(self, obj):
        return f"Room {obj.room.room_number} - Bed {obj.bed.bed_number}"



class StudentRoomIssuesSerializer(serializers.ModelSerializer):
    issue_type_display = serializers.CharField(source="get_issue_type_display", read_only=True)
    resolution_status_display = serializers.CharField(source="get_resolution_status_display", read_only=True)
    class Meta:
        model = StudentRoomIssues
        fields = [
            "issue_id",
            "student",
            "room",
            "issue_type",
            "issue_type_display",
            "issue_description",
            "reported_at",
            "resolution_status",
            "resolution_status_display",
        ]
        read_only_fields = ["issue_id", "reported_at"]


class StudentGetRoomIssuesSerializer(serializers.ModelSerializer):
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    class Meta:
        model = StudentRoomIssues
        fields = [
            "issue_id",
            "student",
            "room",
            "room_number",
            "student_name",
            "issue_type",
            "issue_description",
            "reported_at",
            "resolution_status",
        ]
        