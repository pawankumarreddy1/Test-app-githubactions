from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.hostelmanagement.models import Bed, Building, Floor, Room
from apps.hostelmanagement.serializers import BedSerializer
from .models import RoomAllocation, StudentRoomIssues
from .serializers import RoomAllocationSerializer, AllocateBedSerializer, StudentGetRoomIssuesSerializer, StudentRoomIssuesSerializer
from apps.hostelmanagement.serializers import BedSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from apps.hostelmanagement.models import Bed

class AllocateBedView(APIView):
    def post(self, request):
        serializer = AllocateBedSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                bed = serializer.validated_data["bed"]
                student = serializer.validated_data["student"]

                # Check if bed is already occupied
                if bed.is_occupied:
                    return Response(
                        {"error": f"Bed {bed.bed_number} in Room {bed.room.room_number} is already occupied"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Check if student already has a bed
                existing_bed = Bed.objects.filter(student=student).first()
                if existing_bed:
                    return Response(
                        {"error": f"Student already allocated to Bed {existing_bed.bed_number} in Room {existing_bed.room.room_number}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Allocate student to bed
                bed.student = student
                bed.save()

                return Response(
                    {
                        "message": "Bed allocated successfully",
                        "bed": {
                            "bed_id": str(bed.bed_id),
                            "bed_number": bed.bed_number,
                            "room_number": bed.room.room_number,
                            "is_occupied": bed.is_occupied,
                            "student": {
                                "id": str(student.user_id),
                                "name": student.full_name,
                                "phone": student.phone,
                            },
                        },
                        "room_status": {
                            "room_number": bed.room.room_number,
                            "is_available": bed.room.is_available,
                            "occupied_beds": bed.room.beds.filter(is_occupied=True).count(),
                            "total_beds": bed.room.total_beds,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllocatedBedsStudentView(APIView):
    def get(self, request, student_id):
        beds = Bed.objects.filter(student_id=student_id)
        serializer = BedSerializer(beds, many=True)
        return Response(serializer.data)

class DeallocateBedView(APIView):
    def delete(self, request, allocation_id):
        try:
            with transaction.atomic():
                allocation = RoomAllocation.objects.get(allocation_id=allocation_id)
                bed = allocation.bed
                room = allocation.room

                # Mark bed as unoccupied
                bed.is_occupied = False
                bed.save()

                # Delete allocation
                allocation.delete()

                return Response(
                    {
                        "message": "Bed deallocated successfully",
                        "room_status": {
                            "room_number": room.room_number,
                            "is_available": room.is_available,
                            "occupied_beds": room.beds.filter(is_occupied=True).count(),
                            "total_beds": room.total_beds,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

        except RoomAllocation.DoesNotExist:
            return Response({"error": "Allocation not found"}, status=status.HTTP_404_NOT_FOUND)


class AllocationListView(APIView):
    def get(self, request):
        allocations = RoomAllocation.objects.all()

        # Filter by hostel
        hostel_id = request.query_params.get("hostel_id")
        if hostel_id:
            allocations = allocations.filter(hostel__hostel_id=hostel_id)

        # Filter by student
        student_id = request.query_params.get("student_id")
        if student_id:
            allocations = allocations.filter(student__id=student_id)

        # Filter by room
        room_id = request.query_params.get("room_id")
        if room_id:
            allocations = allocations.filter(room__room_id=room_id)

        serializer = RoomAllocationSerializer(allocations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllocationDetailView(APIView):
    def get(self, request, allocation_id):
        try:
            allocation = RoomAllocation.objects.get(allocation_id=allocation_id)
            serializer = RoomAllocationSerializer(allocation)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RoomAllocation.DoesNotExist:
            return Response({"error": "Allocation not found"}, status=status.HTTP_404_NOT_FOUND)


class AvailableBedsView(APIView):
    def get(self, request):  
        beds = Bed.objects.filter(is_occupied=False)
        # Filter by hostel
        hostel_id = request.query_params.get("hostel_id")
        if hostel_id:
            beds = beds.filter(room__floor__building__hostel__hostel_id=hostel_id)

        # Filter by building
        building_id = request.query_params.get("building_id")
        if building_id:
            beds = beds.filter(room__floor__building__building_id=building_id)

        # Filter by floor
        floor_id = request.query_params.get("floor_id")
        if floor_id:
            beds = beds.filter(room__floor__floor_id=floor_id)

        # Filter by room
        room_id = request.query_params.get("room_id")
        if room_id:
            beds = beds.filter(room__room_id=room_id)

        serializer = BedSerializer(beds, many=True)
        return Response(
            {"available_beds_count": beds.count(), "beds": serializer.data},
            status=status.HTTP_200_OK,
        )

class RoomStatusView(APIView):
    def get(self, request, room_id):
        try:
            from apps.hostelmanagement.serializers import RoomSerializer
            room = Room.objects.get(room_id=room_id)
            allocations = RoomAllocation.objects.filter(room=room)
            serializer = RoomSerializer(room)
            allocation_serializer = RoomAllocationSerializer(allocations, many=True)
            # Reliable occupancy numbers:
            occupied_beds = Bed.objects.filter(room=room, is_occupied=True).count()
            total_beds = room.total_beds or 0
            available_beds = max(0, total_beds - occupied_beds)
            is_fully_occupied = available_beds == 0

            return Response(
                {
                    "room_details": serializer.data,
                    "allocations": allocation_serializer.data,
                    "occupancy_summary": {
                        "total_beds": total_beds,
                        "occupied_beds": occupied_beds,
                        "available_beds": available_beds,
                        "is_fully_occupied": is_fully_occupied,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)


def ensure_beds_for_room(room):
    existing_beds = Bed.objects.filter(room=room).count()
    missing_beds = room.total_beds - existing_beds
    for i in range(1, missing_beds + 1):
        Bed.objects.create(room=room, bed_number=str(existing_beds + i), is_occupied=False)


class AvailableBedsByBuildingView(APIView):
    def get(self, request, building_id):
        try:
            building = Building.objects.get(building_id=building_id)
            floors = Floor.objects.filter(building=building)

            result = {
                "building_id": str(building.building_id),
                "building_name": building.building_name,
                "floors": [],
            }

            for floor in floors:
                floor_data = {
                    "floor_id": str(floor.floor_id),
                    "floor_number": floor.floor_number,
                    "rooms": [],
                }

                rooms = Room.objects.filter(floor=floor)
                for room in rooms:
                    available_beds = Bed.objects.filter(room=room, is_occupied=False)
                    bed_serializer = BedSerializer(available_beds, many=True)

                    room_data = {
                        "room_id": str(room.room_id),
                        "room_number": room.room_number,
                        "total_beds": room.total_beds,
                        "available_beds_count": available_beds.count(),
                        "available_beds": bed_serializer.data,
                    }
                    floor_data["rooms"].append(room_data)

                result["floors"].append(floor_data)

            return Response(result, status=status.HTTP_200_OK)

        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)





class StudentRoomIssueListCreateView(APIView):
    def get(self, request):
        issues = StudentRoomIssues.objects.all().order_by("-reported_at")
        serializer = StudentGetRoomIssuesSerializer(issues, many=True)
       
        return Response(serializer.data)

   
    def post(self, request):
        serializer = StudentRoomIssuesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET issues by student_id
class StudentRoomIssueByStudentView(APIView):
    def get(self, request, student_id):
        issues = StudentRoomIssues.objects.filter(student_id=student_id).order_by("-reported_at")
        serializer = StudentGetRoomIssuesSerializer(issues, many=True)
        return Response(serializer.data)


# PUT update issue (only by student who created it)
class StudentRoomIssueUpdateView(APIView):

    def put(self, request, issue_id):
        issue = get_object_or_404(StudentRoomIssues, issue_id=issue_id)
        student_id = request.data.get("student")

        if str(issue.student_id) != str(student_id):
            return Response({"error": "You cannot update another student's issue"}, status=status.HTTP_403_FORBIDDEN)

        serializer = StudentRoomIssuesSerializer(issue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
