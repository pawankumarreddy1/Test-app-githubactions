from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime
from django.db import models
from django.db.models import Q, Sum
from .serializers import CollectFeeSerializer
from .models import CollectFee
from apps.hostelmanagement.models import Student, Bed
from rest_framework.pagination import PageNumberPagination


class CollectFeeView(APIView):
    def post(self, request):
        serializer = CollectFeeSerializer(data=request.data)
        if serializer.is_valid():
            collect_fee = serializer.save()
            student = collect_fee.student
            bed = student.allocated_bed
            room = getattr(bed, "room", None)

            # Build the response dynamically
            student_details = {
                "student_id": str(student.student_id),
                "full_name": student.student_name,
            }

            allocation_details = {
                "room_number": getattr(room, "room_number", "N/A"),
                "bed_number": getattr(bed, "bed_number", "N/A"),
                "payment_status": "paid",
            }

            # Calculate next_due_amount dynamically
            monthly_rent = 0
            if bed and room and room.monthly_rent:
                try:
                    monthly_rent = int(float(room.monthly_rent))
                except (ValueError, TypeError):
                    monthly_rent = 0
            next_due_amount = max(0, monthly_rent - int(collect_fee.amount))
            
            balance_summary = {
                "total_paid": int(collect_fee.amount),
                "total_due": 0,
                "next_due_date": (
                    timezone.now().date().replace(day=8)
                    + timezone.timedelta(days=30)
                ).isoformat(),
                "next_due_amount": next_due_amount,
            }

            payment_data = {
                "payment_id": f"payment_{str(collect_fee.fee_id)[:8]}",
                "amount": int(collect_fee.amount),
                "payment_type": collect_fee.payment_type.lower(),
                "payment_method": collect_fee.payment_method,
                "status": "completed",
            }

            response_data = {
                "success": True,
                "message": "Payment collected successfully",
                "data": {
                    "payment": payment_data,
                    "student_details": student_details,
                    "allocation_details": allocation_details,
                    "balance_summary": balance_summary,
                },
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    class StandardResultsSetPagination(PageNumberPagination):
        page_size = 10  # default items per page
        page_size_query_param = 'page_size'  # allow ?page_size=20

    
    pagination_class = StandardResultsSetPagination


    def get(self, request): 
        building_id = request.query_params.get("building_id")
        month_param = request.query_params.get("month")  # e.g. "Oct-2025"
        search_query = request.query_params.get("search")
        student_id = request.query_params.get("student_id")

        if not building_id:
            return Response(
                {"error": "building_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if month_param:
                month_number = datetime.strptime(month_param[:3].title(), "%b").month
                year_number = int(month_param[-4:])
            else:
                now = timezone.now()
                month_number = now.month
                year_number = now.year
        except Exception:
            return Response(
                {"error": "Invalid month format. Use 'Jan-2025'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        students_with_fees = Student.objects.filter(
            allocated_bed__room__floor__building_id=building_id,
            fees__payment_date__year=year_number,
            fees__payment_date__month=month_number,
        ).select_related(
            'allocated_bed__room__floor__building__hostel'
        ).distinct()

        if student_id:
            students_with_fees = students_with_fees.filter(student_id=student_id)

        if search_query:
            students_with_fees = students_with_fees.filter(
                Q(student_name__icontains=search_query) |
                Q(allocated_bed__room__room_number__icontains=search_query)
            )
        
        # --- Prepare paginated results ---
        paginator = self.pagination_class()
        paginated_students = paginator.paginate_queryset(students_with_fees, request)
        
        data = []
        for student in students_with_fees:
            fee_for_month = (
                CollectFee.objects.filter(
                    student=student,
                    payment_date__year=year_number,
                    payment_date__month=month_number,
                )
                .order_by("-payment_date", "-updated_at")
            )

            if not fee_for_month.exists():
                continue

            bed = student.allocated_bed
            room = bed.room if bed else None

            for fee in fee_for_month:
                data.append({
                    "student_id": str(student.student_id),
                    "student_name": student.student_name,
                    "room_number": room.room_number if room else "N/A",
                    "bed_number": bed.bed_number if bed else "N/A",
                    "amount": int(fee.amount),
                    "mode": fee.payment_method.capitalize(),
                    "payment_status": "Paid",
                    "payment_date": fee.payment_date.strftime("%Y-%m-%d"),
                    "fee_id": str(fee.fee_id),
                })

        return Response({
            "success": True,
            "month": f"{datetime(year_number, month_number, 1).strftime('%b-%Y')}",
            "building_id": building_id,
            "count": len(data),
            "data": data,
        }, status=status.HTTP_200_OK)
    


     # ---------------- PUT/PATCH: Update collected fee ----------------
    def put(self, request, fee_id):
        try:
            collect_fee = CollectFee.objects.get(fee_id=fee_id)
        except CollectFee.DoesNotExist:
            return Response(
                {"error": "Fee record not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CollectFeeSerializer(collect_fee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_at=timezone.now())
            return Response(
                {
                    "success": True,
                    "message": "Fee record updated successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class FeeDashboardView(APIView):
    def get(self, request):
        building_id = request.query_params.get("building_id")
        month_param = request.query_params.get("month")

        if not building_id:
            return Response({"error": "building_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if month_param:
            try:
                month_number = datetime.strptime(month_param[:3], "%b").month
                year_number = int(month_param[-4:])
            except Exception:
                return Response(
                    {"error": "Invalid month format. Use 'Oct-2025'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            now = timezone.now()
            month_number = now.month
            year_number = now.year

        students = Student.objects.filter(
            allocated_bed__room__floor__building=building_id
        )
        total_students = students.count()

        all_beds = Bed.objects.filter(
            room__floor__building=building_id
        )

        total_expected = 0
        beds_with_rent = 0

        for bed in all_beds:
            rent_value = bed.monthly_rent
            if rent_value and str(rent_value).strip():
                try:
                    bed_rent = int(float(rent_value))
                    total_expected += bed_rent
                    beds_with_rent += 1
                except (ValueError, TypeError):
                    continue

        fees = CollectFee.objects.filter(
            student__in=students,
            payment_date__month=month_number,
            payment_date__year=year_number,
        )

        total_collected = 0
        paid_students = 0

        for student in students:
            student_collected = (
                fees.filter(student=student).aggregate(total=Sum("amount"))["total"]
                or 0
            )
            total_collected += int(student_collected)
            if student_collected > 0:
                paid_students += 1

        pending_amount = total_expected - total_collected
        if pending_amount < 0:
            pending_amount = 0

        today = timezone.now().date()
        overdue_students = 0
        if today.day > 10:
            overdue_students = total_students - paid_students

        return Response(
            {
                "success": True,
                "month": f"{datetime(year_number, month_number, 1).strftime('%b-%Y')}",
                "building_id": building_id,
                "summary": {
                    "total_collected": int(total_collected),
                    "pending_amount": int(pending_amount),
                    "paid_students": paid_students,
                    "total_students": total_students,
                    "paid_percentage": (
                        f"{(paid_students / total_students * 100):.0f}%"
                        if total_students else "0%"
                    ),
                    "overdue": overdue_students,
                },
            },
            status=status.HTTP_200_OK,
        )
