from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Mess, Meal
from .serializers import MessSerializer, MealSerializer

class MessView(APIView):
    # ---------------------- CREATE or UPDATE ----------------------
    def post(self, request):
        building_id = request.data.get("building_id")
        meals_data = request.data.get("meals", [])

        # Check if Mess already exists for this building
        mess, created = Mess.objects.get_or_create(building_id=building_id)

        # Create or update each meal under this mess
        for meal_data in meals_data:
            meal_obj, _ = Meal.objects.update_or_create(
                mess=mess,
                meal=meal_data["meal"],
                defaults={
                    "timing": meal_data.get("timing", ""),
                    "status": meal_data.get("status", "Available"),
                    "menu": meal_data.get("menu", []),
                },
            )

        serializer = MessSerializer(mess)
        return Response(
            {
                "success": True,
                "message": "Mess created/updated successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # ---------------------- GET Mess Data ----------------------
    def get(self, request):
        building_id = request.query_params.get("building_id")
        if not building_id:
            return Response({"success": False, "message": "building_id is required"}, status=400)

        try:
            mess = Mess.objects.get(building_id=building_id)
            serializer = MessSerializer(mess)
            return Response(
                {"success": True, "message": "Mess settings retrieved successfully", "data": serializer.data},
                status=200,
            )
        except Mess.DoesNotExist:
            return Response({"success": False, "message": "Mess not found"}, status=404)

    # ---------------------- UPDATE Specific Meals ----------------------
    def put(self, request):
        building_id = request.data.get("building_id")
        meals_data = request.data.get("meals", [])

        try:
            mess = Mess.objects.get(building_id=building_id)
        except Mess.DoesNotExist:
            return Response({"success": False, "message": "Mess not found"}, status=404)

        # Update or create meals
        for meal_data in meals_data:
            Meal.objects.update_or_create(
                mess=mess,
                meal=meal_data["meal"],
                defaults={
                    "timing": meal_data.get("timing", ""),
                    "status": meal_data.get("status", "Available"),
                    "menu": meal_data.get("menu", []),
                },
            )

        serializer = MessSerializer(mess)
        return Response(
            {"success": True, "message": "Mess data updated successfully", "data": serializer.data},
            status=200,
        )
