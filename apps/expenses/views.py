from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from .models import Expense
from .serializers import ExpenseSerializer
from apps.hostelmanagement.models import Building
import uuid

# ---------------- CREATE MULTIPLE EXPENSES FOR A BUILDING ----------------
class ExpenseCreateAPIView(APIView):
    def post(self, request, building_id):
        try:
            building = Building.objects.get(building_id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        expenses_data = request.data
        # Create a new list with building added
        for exp in expenses_data:
            exp["building"] = str(building.building_id)  # UUID field expects a string

        serializer = ExpenseSerializer(data=expenses_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Expenses created successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# ---------------- GET ALL EXPENSES FOR A BUILDING (PAGINATED) ----------------
class ExpenseByBuildingAPIView(APIView):
    def get(self, request, building_id):
        # Get building
        try:
            building = Building.objects.get(building_id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        # Query params
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        sort = request.query_params.get("sort", "-date")
        month = request.query_params.get("month")  # format: "YYYY-MM"

        # Filter expenses by building
        expenses = Expense.objects.filter(building=building)

        # Filter by month if provided
        if month:
            try:
                year, month_num = map(int, month.split("-"))
                expenses = expenses.filter(date__year=year, date__month=month_num)
            except ValueError:
                return Response({"error": "Invalid month format. Use YYYY-MM"}, status=status.HTTP_400_BAD_REQUEST)

        # Order
        expenses = expenses.order_by(sort)

        # Pagination
        paginator = Paginator(expenses, page_size)
        paginated_data = paginator.get_page(page)

        serializer = ExpenseSerializer(paginated_data, many=True)
        total_amount = sum(e.amount for e in expenses)

        return Response(
            {
                "building_id": building_id,
                "building_name": building.building_name,
                "total_records": paginator.count,
                "page": page,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "total_amount": total_amount,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

# ---------------- UPDATE EXPENSE FOR A BUILDING BY EXPENSE UUID ----------------
class ExpenseUpdateAPIView(APIView):

    def put(self, request):
        building_id = request.query_params.get("building_id")

        if not building_id:
            return Response(
                {"error": "building_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            building = Building.objects.get(building_id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        if not isinstance(data, list):
            # If single object sent, wrap it in a list for uniform processing
            data = [data]

        updated_expenses = []
        errors = []

        for item in data:
            expense_uuid = item.get("expense_uuid")
            if not expense_uuid:
                errors.append({"error": "expense_uuid is required in each item", "item": item})
                continue

            try:
                expense = Expense.objects.get(expense_uuid=expense_uuid, building=building)
            except Expense.DoesNotExist:
                errors.append({"error": "Expense not found", "expense_uuid": expense_uuid})
                continue

            serializer = ExpenseSerializer(expense, data=item, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_expenses.append(serializer.data)
            else:
                errors.append({"expense_uuid": expense_uuid, "errors": serializer.errors})

        return Response(
            {
                "updated_expenses": updated_expenses,
                "errors": errors,
            },
            status=status.HTTP_200_OK,
        )


# ---------------- DELETE EXPENSE FOR A BUILDING BY EXPENSE UUID ----------------
class ExpenseDeleteAPIView(APIView):
    def delete(self, request):
        building_id = request.query_params.get("building_id")
        expense_id = request.query_params.get("expense_id")

        if not building_id or not expense_id:
            return Response(
                {"error": "building_id and expense_id are required query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            building = Building.objects.get(building_id=building_id)
        except Building.DoesNotExist:
            return Response({"error": "Building not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            expense = Expense.objects.get(expense_uuid=expense_id, building=building)
            expense.delete()
            return Response({"message": "Expense deleted successfully"}, status=status.HTTP_200_OK)
        except Expense.DoesNotExist:
            return Response({"error": "Expense not found"}, status=status.HTTP_404_NOT_FOUND)