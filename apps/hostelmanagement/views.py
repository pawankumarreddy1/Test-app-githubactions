from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.hostelinfo.models import User
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from .models import Bed, Building, Floor, Hostel, Room, Inventory, RoomInventory, Student
from .serializers import (
    BedSerializer,
    BuildingInventorySerializer,
    BuildingSerializer,
    FloorSerializer,
    HostelSerializer,
    RoomSerializer,
    BulkRoomUpdateSerializer,
    InventorySerializer,
    BulkFloorTotalRoomsUpdateSerializer,
    StudentSimpleSerializer,
)


# ------------------ HOSTEL API ------------------
class HostelView(APIView):
    def get(self, request):
        hostels = Hostel.objects.all()
        serializer = HostelSerializer(hostels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HostelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HostelDetailView(APIView):
    def get(self, request, hostel_id):
        try:
            hostel = Hostel.objects.get(hostel_id=hostel_id)
            serializer = HostelSerializer(hostel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, hostel_id):
        try:
            hostel = Hostel.objects.get(hostel_id=hostel_id)
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = HostelSerializer(hostel, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, hostel_id):
        try:
            hostel = Hostel.objects.get(hostel_id=hostel_id)
            hostel.delete()
            return Response({"message": f"Hostel with id {hostel_id} deleted successfully"}, status=status.HTTP_200_OK)
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found"}, status=status.HTTP_404_NOT_FOUND)
    

# ------------------ HOSTEL BY OWNER API ------------------
class HostelByOwnerView(APIView):
    def get(self, request, owner_id):
        hostels = Hostel.objects.filter(owner=owner_id)
        serializer = HostelSerializer(hostels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ------------------ BUILDING API ------------------
class BuildingView(APIView):
    def get(self, request):
        buildings = Building.objects.all()
        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BuildingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BuildingByHostelView(APIView):
    def get(self, request, hostel_id):
        buildings = Building.objects.filter(hostel=hostel_id)
        serializer = BuildingSerializer(buildings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BuildingDetailView(APIView):
    def get(self, request, building_id):
        try:
            building = Building.objects.get(building_id=building_id)
            serializer = BuildingSerializer(building)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, building_id):
        try:
            building = Building.objects.get(building_id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BuildingSerializer(building, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, building_id):
        try:
            building = Building.objects.get(building_id=building_id)
            building.delete()
            return Response({"message": f"Building with id {building_id} deleted successfully"}, status=status.HTTP_200_OK)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)


# ------------------ FLOOR API ------------------
class FloorView(APIView):
    def get(self, request):
        floors = Floor.objects.all()
        serializer = FloorSerializer(floors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FloorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FloorByBuildingView(APIView):
    def get(self, request, building_id):
        floors = Floor.objects.filter(building=building_id)
        serializer = FloorSerializer(floors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FloorDetailView(APIView):
    def get(self, request, floor_id):
        try:
            floor = Floor.objects.get(floor_id=floor_id)
            serializer = FloorSerializer(floor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Floor.DoesNotExist:
            return Response({"error": "Floor not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, floor_id):
        try:
            floor = Floor.objects.get(floor_id=floor_id)
        except Floor.DoesNotExist:
            return Response({"error": "Floor not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FloorSerializer(floor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, floor_id):
        try:
            floor = Floor.objects.get(floor_id=floor_id)
            floor.delete()
            return Response({"message": f"Floor with id {floor_id} deleted successfully"}, status=status.HTTP_200_OK)
        except Floor.DoesNotExist:
            return Response({"error": "Floor not found"}, status=status.HTTP_404_NOT_FOUND)


# ------------------ ROOM API ------------------
class RoomView(APIView):
    def get(self, request):
        status_param = request.query_params.get("status") 
        rooms = Room.objects.all()

        if status_param == "vacant":
            # Rooms that have at least 1 empty bed
            rooms = rooms.filter(beds__is_occupied=False).distinct()

        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        many = isinstance(request.data, list)
        serializer = RoomSerializer(data=request.data, many=many)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoomByFloorView(APIView):
    def get(self, request, floor_id):
        rooms = Room.objects.filter(floor=floor_id)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomDetailView(APIView):
    def get(self, request, room_id):
        try:
            room = Room.objects.get(room_id=room_id)
            serializer = RoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, room_id):
        try:
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoomSerializer(room, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, room_id):
        try:
            room = Room.objects.get(room_id=room_id)
            room.delete()
            return Response({"message": f"Room with id {room_id} deleted successfully"}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)


# ------------------ BED API ------------------
class BedView(APIView):
    def get(self, request):
        status_param = request.query_params.get("status")
        # beds = Bed.objects.all()
        rooms = Room.objects.prefetch_related('beds', 'floor__building__hostel').all()
        if status_param == "empty":
            rooms = rooms.filter(beds__is_occupied=False).distinct()
        elif status_param == "booked":
            rooms = rooms.filter(beds__is_occupied=True).distinct()
        serializer = RoomSerializer(rooms, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BedByRoomView(APIView):
    def get(self, request, room_id):
        beds = Bed.objects.filter(room=room_id)
        serializer = BedSerializer(beds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BedDetailView(APIView):
    def get(self, request, bed_id):
        try:
            bed = Bed.objects.get(bed_id=bed_id)
            serializer = BedSerializer(bed)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Bed.DoesNotExist:
            return Response({"error": "Bed not found"}, status=status.HTTP_404_NOT_FOUND)


class AvailableBedsView(APIView):
    def get(self, request):
        building_id = request.query_params.get("building_id")
        if not building_id:
            return Response({"error": "building_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        beds = Bed.objects.filter(
            is_occupied=False,
            room__floor__building__building_id=building_id,
        ).select_related(
            "room",
            "room__floor",
            "room__floor__building",
            "room__floor__building__hostel",
        )

        room_id = request.query_params.get("room_id")
        floor_id = request.query_params.get("floor_id")
        hostel_id = request.query_params.get("hostel_id")

        if room_id:
            beds = beds.filter(room__room_id=room_id)
        if floor_id:
            beds = beds.filter(room__floor__floor_id=floor_id)
        if hostel_id:
            beds = beds.filter(room__floor__building__hostel__hostel_id=hostel_id)

        serializer = BedSerializer(beds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AvailableBedsView(APIView):
    def get(self, request):
        building_id = request.query_params.get("building_id")
        if not building_id:
            return Response({"error": "building_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        beds = Bed.objects.filter(
            is_occupied=False,
            room__floor__building__building_id=building_id,
        ).select_related(
            "room",
            "room__floor",
            "room__floor__building",
            "room__floor__building__hostel",
        )

        room_id = request.query_params.get("room_id")
        floor_id = request.query_params.get("floor_id")
        hostel_id = request.query_params.get("hostel_id")

        if room_id:
            beds = beds.filter(room__room_id=room_id)
        if floor_id:
            beds = beds.filter(room__floor__floor_id=floor_id)
        if hostel_id:
            beds = beds.filter(room__floor__building__hostel__hostel_id=hostel_id)

        serializer = BedSerializer(beds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BulkRoomUpdateAPIView(APIView):
    """
    Bulk update rooms API (PUT only)
    """
    def put(self, request, *args, **kwargs):
        serializer = BulkRoomUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()  # calls update() in serializer

        updated_rooms = result.get("updated_rooms", [])
        not_found = result.get("not_found", [])

        return Response(
            {
                "message": f"{len(updated_rooms)} rooms updated successfully",
                "updated_rooms": [str(room.room_id) for room in updated_rooms],
                "not_found": not_found,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, *args, **kwargs):
        serializer = BulkRoomUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        updated_rooms = result.get("updated_rooms", [])
        not_found = result.get("not_found", [])

        return Response(
            {
                "message": f"{len(updated_rooms)} rooms updated successfully",
                "updated_rooms": [str(room.room_id) for room in updated_rooms],
                "not_found": not_found,
            },
            status=status.HTTP_200_OK,
        )

class Deleteinventory(APIView):
    def delete(self, request, room_id):
        try:
            # Ensure the room exists
            room = Room.objects.get(room_id=room_id)
        except Room.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete all RoomInventory records linked to this room
        deleted_count, _ = RoomInventory.objects.filter(room=room).delete()

        return Response(
            {
                "message": f"Deleted {deleted_count} inventory records for room {room.room_number}."
            },
            status=status.HTTP_200_OK
        )
        





class FloorTotalRoomsUpdateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        floors_data = []
        
        # Extract floor data from request
        for item in request.data:
            if "floor" in item and "total_rooms" in item:
                floors_data.append({
                    "floor": item["floor"],
                    "total_rooms": item["total_rooms"]
                })
        
        if not floors_data:
            return Response(
                {"error": "No valid floor data provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate the data
        serializer = BulkFloorTotalRoomsUpdateSerializer(data={"floors_data": floors_data})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Use validated data instead of raw input data
        validated_floors_data = serializer.validated_data["floors_data"]
        
        results = []
        
        for floor_data in validated_floors_data:
            floor = floor_data["floor"]  # This is already the Floor object from serializer validation
            new_total_rooms = int(floor_data["total_rooms"])  # Ensure integer type
            old_total_rooms = floor.total_rooms or 0
            current_room_count = floor.rooms.count()
            
            # Update the floor's total_rooms field
            # The signal will automatically create rooms if needed
            floor.total_rooms = new_total_rooms
            floor.save(update_fields=['total_rooms'])
            
            # Count rooms created by checking the room count after save
            final_room_count = floor.rooms.count()
            rooms_created = final_room_count - current_room_count
                
            results.append({
                "floor_id": str(floor.floor_id),
                "floor_number": floor.floor_number,
                "building_name": floor.building.building_name,
                "previous_total_rooms": old_total_rooms,
                "current_room_count": current_room_count,
                "new_total_rooms": new_total_rooms,
                "final_room_count": final_room_count,
                "rooms_created": rooms_created,
                "status": "success"
            })
        
        return Response({
            "message": "Floor updates completed successfully.",
            "results": results
        }, status=status.HTTP_200_OK)


# ------------------ INVENTORY API ------------------
# ---------------- GET all inventories (flat list) ----------------
class InventoryListView(APIView):
    def get(self, request):
        # Get all inventories with related room data
        inventories = Inventory.objects.select_related('room', 'builiding', 'hostel').all()
        
        # Group by common fields and organize by room
        grouped_data = self.group_inventories_by_common_fields(inventories)
        
        return Response(grouped_data, status=200)
    
    def group_inventories_by_common_fields(self, inventories):
        # Structure to hold our final response
        response_data = {}
        
        for inventory in inventories:
            # Use the correct field names from your model
            common_key = f"{inventory.owner_id}_{inventory.hostel_id}_{inventory.builiding_id}"
            
            if common_key not in response_data:
                # Initialize the common data structure
                response_data[common_key] = {
                    "owner_id": inventory.owner_id,
                    "hostel_id": inventory.hostel_id,
                    "building_id": inventory.builiding_id,  # Use builiding_id here
                    "rooms": []
                }
            
            # Find if this room already exists in the rooms list
            room_exists = False
            for room_data in response_data[common_key]["rooms"]:
                if room_data["room_id"] == inventory.room.room_id:
                    # Room exists, add inventory item
                    room_data["inventory_items"].append({
                        "inventory_id": str(inventory.inventory_id),
                        "name": inventory.inventory_type,
                        "quantity": inventory.quantity
                    })
                    room_exists = True
                    break
            
            # If room doesn't exist, create new room entry
            if not room_exists:
                response_data[common_key]["rooms"].append({
                    "room_id": inventory.room.room_id,
                    "room_number": inventory.room.room_number,
                    "inventory_items": [{
                        "inventory_id": str(inventory.inventory_id),
                        "name": inventory.inventory_type,
                        "quantity": inventory.quantity
                    }]
                })
        return list(response_data.values())
# ---------------- GET by inventory_id ----------------
class InventoryDetailView(APIView):
    def get(self, request, inventory_id):
        try:
            inventory = Inventory.objects.get(inventory_id=inventory_id)
            serializer = InventorySerializer(inventory)
            return Response(serializer.data, status=200)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory not found"}, status=404)

    def put(self, request, inventory_id):
        try:
            inventory = Inventory.objects.get(inventory_id=inventory_id)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory not found"}, status=404)
        serializer = InventorySerializer(inventory, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, inventory_id):
        try:
            inventory = Inventory.objects.get(inventory_id=inventory_id)
            inventory.delete()
            return Response({"message": "Inventory deleted successfully"}, status=200)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory not found"}, status=404)

# ---------------- GET inventories by building (rooms grouped) ----------------
class BuildingRoomsInventoryView(APIView):
    def get(self, request, building_id):
        rooms = Room.objects.filter(building_id=building_id).order_by("room_number")
        if not rooms.exists():
            return Response({"error": "No rooms found for this building"}, status=404)
        hostel_id = str(rooms.first().hostel.id)
        rooms_data = []
        for room in rooms:
            inventories = Inventory.objects.filter(room=room)
            inventory_data = [{"inventory_id": str(inv.inventory_id), "name": inv.inventory_type, "quantity": inv.quantity} for inv in inventories]
            rooms_data.append({
                "inventory_id": str(room.id),
                "room_id": str(room.id),
                "room_number": room.room_number,
                "inventory_type": inventory_data
            })
        response_data = {
            "building_id": building_id,
            "hostel_id": hostel_id,
            "rooms": rooms_data
        }
        return Response(response_data, status=200)

# ---------------- GET/PUT inventories by room_id ----------------
class RoomInventoryDetailView(APIView):
    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)
        inventories = Inventory.objects.filter(room=room)
        inventory_data = [{"inventory_id": str(inv.inventory_id), "name": inv.inventory_type, "quantity": inv.quantity} for inv in inventories]
        response_data = {
            "building_id": str(room.building.id),
            "hostel_id": str(room.hostel.id),
            "rooms": [
                {
                    "inventory_id": str(room.id),
                    "room_id": str(room.id),
                    "room_number": room.room_number,
                    "inventory_type": inventory_data
                }
            ]
        }
        return Response(response_data, status=200)

    def put(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)
        inventory_items = request.data.get("inventory_type", [])
        for item in inventory_items:
            Inventory.objects.update_or_create(
                room=room,
                inventory_type=item.get("name"),
                defaults={
                    "quantity": item.get("quantity", 0),
                    "owner": request.user,
                    "hostel": room.hostel,
                    "builiding": room.building,
                    "Floor": room.floor
                }
            )
        return Response({"message": "Room inventories updated successfully"}, status=200)

# ---------------- Bulk POST inventories ----------------
class BulkInventoryCreateView(APIView):
    def post(self, request, *args, **kwargs):
        building_id = request.data.get("building_id")
        hostel_id = request.data.get("hostel_id")
        rooms_data = request.data.get("rooms", [])
        owner_id = request.data.get("owner_id")  # Get owner from request
        
        if not building_id or not hostel_id or not rooms_data or not owner_id:
            return Response(
                {"error": "building_id, hostel_id, owner_id, and rooms are required"},
                status=400
            )

        # Verify owner exists
        try:
            owner = User.objects.get(pk=owner_id)
        except User.DoesNotExist:
            return Response(
                {"error": f"Owner with id {owner_id} not found"}, 
                status=400
            )

        # Verify building exists and belongs to hostel
        try:
            building = Building.objects.get(pk=building_id, hostel_id=hostel_id)
        except Building.DoesNotExist:
            return Response(
                {"error": f"Building {building_id} not found in hostel {hostel_id}"}, 
                status=400
            )

        bulk_inventories = []
        
        for room_data in rooms_data:
            room_id = room_data.get("room_id")
            inventory_items = room_data.get("inventory_items", [])
            
            if not room_id:
                return Response(
                    {"error": "room_id is required for each room"}, 
                    status=400
                )
            
            try:
                # Verify room exists in the specified building
                room = Room.objects.get(
                    pk=room_id,
                    floor__building__pk=building_id
                )
            except Room.DoesNotExist:
                return Response(
                    {"error": f"Room {room_id} not found in building {building_id}"}, 
                    status=400
                )

            # Add inventory items for this room
            for item in inventory_items:
                bulk_inventories.append(
                    Inventory(
                        owner=owner,  # Use the owner from request
                        hostel_id=hostel_id,
                        builiding_id=building_id,
                        room=room,
                        floor=room.floor,
                        inventory_type=item.get("name"),
                        quantity=item.get("quantity", 0)
                    )
                )

        if not bulk_inventories:
            return Response(
                {"error": "No inventory items to create"}, 
                status=400
            )

        inventories = Inventory.objects.bulk_create(bulk_inventories)

        return Response(
            {
                "message": "Inventories added successfully",
                "rooms_processed": len(rooms_data),
                "total_inventories": len(inventories)
            },
            status=201
        )


# ------------------ ANALYTICS API ------------------
class BedAnalyticsView(APIView):
    def get(self, request, building_id):
        try:
            # Verify building exists
            try:
                building = Building.objects.get(building_id=building_id)
            except Building.DoesNotExist:
                return Response(
                    {"error": "Building not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get beds filtered by building through room relationship
            beds_in_building = Bed.objects.filter(room__floor__building=building)
            
            # Get total bed count for this building
            total_bed_count = beds_in_building.count()
            
            # Get occupied beds count for this building
            total_occupied = beds_in_building.filter(is_occupied=True).count()
            
            # Get available beds count for this building
            total_available = beds_in_building.filter(is_occupied=False).count()
            
            # Verify the math is correct
            if total_bed_count != (total_occupied + total_available):
                # If there's a discrepancy, recalculate available beds
                total_available = total_bed_count - total_occupied
            
            analytics_data = {
                "building_id": str(building_id),
                "building_name": building.building_name,
                "total_bed_count": total_bed_count,
                "total_occupied": total_occupied,
                "total_available": total_available
            }
            
            return Response(analytics_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Error retrieving analytics data: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ---------------- Custom Pagination Class ----------------
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default items per page
    page_size_query_param = 'page_size'  # client can override ?page_size=50

# ---------------- GET student details by building_id ----------------
class StudentDetailsView(APIView):
    pagination_class = StandardResultsSetPagination

    def get(self, request, building_id):
        search_query = (request.query_params.get("search") or "").strip()

        # base queryset: students in the building
        students_qs = Student.objects.filter(
            allocated_bed__room__floor__building__building_id=building_id
        ).select_related(
            # follow single-value relations to avoid extra queries
            "allocated_bed__room__floor__building",
        ).prefetch_related(
            # if your Student -> fees or other m2m exist add them here
        ).distinct()

        # apply search: name, mobile, room number, bed number
        if search_query:
            students_qs = students_qs.filter(
                Q(student_name__icontains=search_query)
                | Q(mobile_number__icontains=search_query)
                | Q(allocated_bed__room__room_number__icontains=search_query)
                | Q(allocated_bed__bed_number__icontains=search_query)
            )

        # if no rows after filtering, return empty paginated structure
        if not students_qs.exists():
            return Response(
                {"count": 0, "next": None, "previous": None, "results": []},
                status=status.HTTP_200_OK,
            )

        # paginate
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(students_qs, request)

        serializer = StudentSimpleSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

# ---------------- GET Inventory details by building_id ----------------
class InventoryDetailsByBuildingView(APIView):
    def get(self, request, building_id):
        try:
            building = Building.objects.prefetch_related(
                'floors__rooms__roominventory_set__inventory'
            ).get(building_id=building_id)
        except Building.DoesNotExist:
            return Response({"detail": "Building not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BuildingInventorySerializer(building)
        return Response(serializer.data, status=status.HTTP_200_OK)