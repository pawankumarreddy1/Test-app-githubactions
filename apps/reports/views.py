from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.hostelmanagement.models import Floor,Bed, Student, Building
from .serializers import FloorSerializer, OccupiedBedSerializer, StudentReportSerializer, TotalBedSerializer, OccupiedBedDetailSerializer
 
class HostelRoomReportView(APIView):
    """
    Returns floors with room hierarchy for a building
    """
    def get(self, request, building_id, *args, **kwargs):
        floors = Floor.objects.filter(building_id=building_id).prefetch_related('rooms__beds')
        serializer = FloorSerializer(floors, many=True)
        return Response(serializer.data)
   
 

class OccupiedBedReportView(APIView):
    """
    Returns all occupied beds for a given building.
    """
    def get(self, request, building_id, *args, **kwargs):
        # Filter beds in the building that are occupied
        beds = Bed.objects.filter(
            student__allocated_bed__isnull=False,  # bed has a student
            room__floor__building_id=building_id
        ).select_related('room')
        # Map student info to beds
        students = Student.objects.filter(allocated_bed__in=beds).select_related('allocated_bed')
        student_dict = {s.allocated_bed_id: s for s in students}
 
        for bed in beds:
            bed.student = student_dict.get(bed.bed_id)
 
        serializer = OccupiedBedSerializer(beds, many=True)
        return Response(serializer.data)
   
 
 
 
class BuildingStudentsReportView(APIView):
    def get(self, request, building_id):
        try:
            building = Building.objects.get(building_id=building_id)
        except Building.DoesNotExist:
            return Response({'detail': 'Building not found.'}, status=status.HTTP_404_NOT_FOUND)
 
        students = Student.objects.filter(
            allocated_bed__room__floor__building=building
        ).select_related('allocated_bed', 'allocated_bed__room', 'allocated_bed__room__floor', 'allocated_bed__room__floor__building')
 
        serializer = StudentReportSerializer(students, many=True)
        return Response({
            'building_id': str(building.building_id),
            'building_name': building.building_name,
            'students': serializer.data
        })
 

class BedReportView(APIView):
    """
    API endpoint to fetch bed information based on type parameter.
    
    Query Parameters:
    - type: 'totalbeds' or 'occupiedbeds'
    - building_id: UUID of the building (required)
    
    Examples:
    - GET /api/reports/bed-report/?type=totalbeds&building_id=<uuid>
    - GET /api/reports/bed-report/?type=occupiedbeds&building_id=<uuid>
    """
    
    def get(self, request):
        # Get query parameters
        report_type = request.query_params.get('type', '').lower()
        building_id = request.query_params.get('building_id')
        
        # Validate required parameters
        if not building_id:
            return Response(
                {"error": "building_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not report_type:
            return Response(
                {"error": "type parameter is required. Use 'totalbeds' or 'occupiedbeds'"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate building exists
        try:
            building = Building.objects.get(building_id=building_id)
        except Building.DoesNotExist:
            return Response(
                {"error": "Building not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Handle different report types
        if report_type == 'totalbeds':
            return self._get_total_beds(building)
        elif report_type == 'occupiedbeds':
            return self._get_occupied_beds(building)
        else:
            return Response(
                {"error": "Invalid type parameter. Use 'totalbeds' or 'occupiedbeds'"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _get_total_beds(self, building):
        """Fetch all beds in the building with their details"""
        beds = Bed.objects.filter(
            room__floor__building=building
        ).select_related('room', 'room__floor', 'room__floor__building').order_by(
            'room__floor__floor_number', 'room__room_number', 'bed_number'
        )
        
        serializer = TotalBedSerializer(beds, many=True)
        
        # Calculate summary statistics
        total_beds_count = beds.count()
        occupied_count = beds.filter(is_occupied=True).count()
        available_count = total_beds_count - occupied_count
        
        return Response({
            "building_id": str(building.building_id),
            "building_name": building.building_name,
            "summary": {
                "total_beds": total_beds_count,
                "occupied_beds": occupied_count,
                "available_beds": available_count
            },
            "beds": serializer.data
        })
    
    def _get_occupied_beds(self, building):
        """Fetch all occupied beds with student details"""
        beds = Bed.objects.filter(
            room__floor__building=building,
            is_occupied=True
        ).select_related('room', 'room__floor', 'room__floor__building').prefetch_related(
            'allocations__student'
        ).order_by('room__floor__floor_number', 'room__room_number', 'bed_number')
        
        serializer = OccupiedBedDetailSerializer(beds, many=True)
        
        return Response({
            "building_id": str(building.building_id),
            "building_name": building.building_name,
            "summary": {
                "occupied_beds_count": beds.count()
            },
            "occupied_beds": serializer.data
        })