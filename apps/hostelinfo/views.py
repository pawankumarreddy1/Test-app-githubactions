import random
import time
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.hostelinfo.models import User, Subscription
from apps.hostelmanagement.models import Student

import logging

logger = logging.getLogger(__name__)

# Utility function to get subscription ID from User model
def get_user_subscription_id(user):
    try:
        subscription = Subscription.objects.filter(user=user).order_by('-created_at').first()
        return str(subscription.subscription_id) if subscription else None
    except Exception as e:
        logger.error(f"Error getting subscription ID for user {user.user_id}: {str(e)}")
        return None

from .serializers import (
    ForgotPasswordSerializer,
    PremiumSubscriptionSerializer,
    ReceiptUploadSerializer,
    ResetPasswordSerializer,
    StudentListSerializer,
    StudentSerializer,
    StudentdetailsSerializer,
    TrialActivationSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

# Temporary in-memory storage for OTPs
OTP_STORE = {}

OTP_EXPIRY_TIME = 60  # 1 minutes

class UserRegisterAPIView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Return the exact format requested
            response_data = {
                "full_name": user.full_name,
                "gender": user.gender,
                "address": user.address,
                "phone": user.phone,
                "email": user.email,
                "password": request.data.get("password", ""),
                "confirm_password": request.data.get("confirm_password", ""),
                "role": user.role
            }
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)


class UserDetailAPIView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.delete()
        return Response({"detail": "User deleted"}, status=status.HTTP_204_NO_CONTENT)


class StudentListAPIView(APIView):
    def get(self, request):
        students = User.objects.filter(role="student")
        logger.info(f"Students: {students}")
        serializer = UserSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ---------------- User Login API ----------------
class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            
            # Get subscription data from Subscription model
            subscription_data = self._get_subscription_data(user)
            
            user_data = {
                "id": str(user.user_id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "phone": user.phone
            }
            
            # Prepare response data
            response_data = {
                "message": "Login successful",
                "user_id": str(user.user_id),
                "role": user.role,
                "user": user_data
            }
            
            # Only include subscription if it has valid data (not null subscription_id)
            if subscription_data.get("subscription_id") is not None:
                response_data["subscription"] = subscription_data
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_subscription_id(self, user):
        """Get subscription ID from Subscription model based on User model"""
        try:
            subscription = Subscription.objects.filter(user=user).order_by('-created_at').first()
            return str(subscription.subscription_id) if subscription else None
        except Exception as e:
            logger.error(f"Error getting subscription ID for user {user.user_id}: {str(e)}")
            return None
    
    def _get_subscription_data(self, user):
        """Get subscription data from Subscription model"""
        print(f"User: {user}")
        try:
            # Get the latest subscription for the user
            subscription = Subscription.objects.filter(user=user).order_by('-created_at').first()
            
            if subscription:
                return {
                    "subscription_id": str(subscription.subscription_id),
                    "account_type": subscription.account_type,
                    "subscription_date": subscription.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end_date": subscription.end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if subscription.end_date else None,
                    "status": "active" if subscription.end_date and subscription.end_date.date() > date.today() else "expired",
                    "features": self._get_features_for_plan(subscription.account_type)
                }
            else:
                # No subscription found, return default data
                return {
                    "subscription_id": None,
                    "account_type": "basic",
                    "subscription_date": None,
                    "end_date": None,
                    "status": "no_subscription",
                    "features": self._get_features_for_plan("basic")
                }
        except Exception as e:
            logger.error(f"Error getting subscription data for user {user.user_id}: {str(e)}")
            return {
                "subscription_id": None,
                "account_type": "basic",
                "subscription_date": None,
                "end_date": None,
                "status": "error",
                "features": self._get_features_for_plan("basic")
            }
    
    def _get_features_for_plan(self, plan_type):
        """Return features based on plan type"""
        if plan_type == "free_trial":
            return [
                "basic_hostel_management",
                "student_registration", 
                "room_allocation",
                "basic_reports",
                "maintenance_tracking"
            ]
        elif plan_type == "premium":
            return [
                "advanced_hostel_management",
                "student_registration",
                "room_allocation", 
                "advanced_reports",
                "maintenance_tracking",
                "financial_analytics",
                "custom_notifications",
                "api_access"
            ]
        else:
            return [
                "basic_hostel_management",
                "student_registration",
                "room_allocation"
            ]


# ---------------- Forgot Password API ----------------
class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]

            otp = str(random.randint(100000, 999999))
            OTP_STORE[email] = {"otp": otp, "timestamp": time.time()}

            # Send OTP via email
            subject = "Password Reset OTP"
            message = f"Your OTP for password reset is: {otp}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            return Response(
                {"message": "OTP sent to your email"}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- Reset Password API ----------------
class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            otp = serializer.validated_data["otp"]
            new_password = serializer.validated_data["new_password"]

            otp_data = OTP_STORE.get(email)
            if not otp_data or otp_data["otp"] != otp:
                return Response({"error": "Invalid or expired OTP"}, status=400)

            # Check if OTP expired
            if time.time() - otp_data["timestamp"] > OTP_EXPIRY_TIME:
                OTP_STORE.pop(email, None)
                return Response({"error": "OTP expired"}, status=400)

            user = get_object_or_404(User, email=email)
            user.password = make_password(new_password)
            user.save()

            OTP_STORE.pop(email, None)
            return Response({"message": "Password reset successful"}, status=200)

        return Response(serializer.errors, status=400)


# ---------------- Resend OTP API ----------------
class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"error": "User with this email does not exist"}, status=404)

        # Throttle: don’t allow resend within 1 minute
        if (
            email in OTP_STORE
            and time.time() - OTP_STORE[email]["timestamp"] < 60
        ):
            return Response(
                {"error": "Please wait before requesting another OTP"},
                status=429,
            )

        otp = str(random.randint(100000, 999999))
        OTP_STORE[email] = {"otp": otp, "timestamp": time.time()}

        subject = "Password Reset OTP (Resent)"
        message = f"Your new OTP for password reset is: {otp}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        return Response({"message": "New OTP sent to your email"}, status=200)


# ---------------- Student List API ----------------
class StudentAPIView(APIView):
    def post(self, request):
        serializer = StudentdetailsSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            if student.allocated_bed:
                bed = student.allocated_bed
                bed.is_occupied = True
                bed.save(update_fields=["is_occupied"])
            return Response({
                "success": True,
                "message": "Student registered and bed allocated successfully",
                "data": StudentdetailsSerializer(student).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, student_id=None):
        if student_id:
            student = get_object_or_404(Student, student_id=student_id)
            serializer = StudentListSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            students = Student.objects.all()
            serializer = StudentListSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    def put(self, request, student_id):
        student = get_object_or_404(Student, student_id=student_id)
        old_bed = student.allocated_bed

        serializer = StudentdetailsSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            updated_student = serializer.save()
            new_bed = updated_student.allocated_bed

            # If bed changed
            if old_bed != new_bed:
                # Free old bed
                if old_bed:
                    old_bed.is_occupied = False
                    old_bed.save(update_fields=["is_occupied"])
                # Occupy new bed
                if new_bed:
                    new_bed.is_occupied = True
                    new_bed.save(update_fields=["is_occupied"])

            return Response({
                "success": True,
                "message": "Student updated successfully",
                "data": StudentdetailsSerializer(updated_student).data
            }, status=status.HTTP_200_OK)
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, student_id):
        student = get_object_or_404(Student, student_id=student_id)
        bed = student.allocated_bed
        student.delete()
        if bed:
            bed.is_occupied = False
            bed.save(update_fields=["is_occupied"])

        return Response({
            "success": True,
            "message": "Student deleted and bed released successfully"
        }, status=status.HTTP_204_NO_CONTENT)
    

class StudentDetailAPIView(APIView):
    def get(self, request, owner_id):
        try:
            owner = User.objects.filter(user_id=owner_id).first()
            if not owner:
                return Response(
                    {"error": f"Owner with ID {owner_id} not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Filter students by owner_id
            students = Student.objects.filter(owner=owner_id)
            print(f"Found {students.count()} students for owner {owner_id}")
            
            # Serialize the data
            serializer = StudentSerializer(students, many=True)
            
            return Response({
                "message": f"Students for owner {owner_id}",
                "count": students.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"Error in StudentDetailAPIView: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching students"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ---------------- Trial Activation API ----------------
class TrialActivationView(APIView):
    def post(self, request):
        """Activate a 30-day free trial for the user"""
        serializer = TrialActivationSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user = User.objects.get(user_id=user_id)
            
            # Create subscription in Subscription model
            subscription = Subscription.objects.create(
                user=user,
                account_type='free_trial',
                end_date=datetime   .now() + timedelta(days=30)
            )
            
            # Update user expiry date
            user.expiry_date = subscription.end_date
            user.save()
            
            # Generate subscription data from Subscription model
            subscription_data = {
                "subscription_id": str(subscription.subscription_id),
                "plan_type": "trial",
                "status": "active",
                "subscription_date": subscription.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_date": subscription.end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if subscription.end_date else None,
                "days_remaining": (subscription.end_date.date() - date.today()).days if subscription.end_date else 0,
                "features": self._get_trial_features()
            }
            
            return Response(
                {
                    "success": True,
                    "message": "Trial subscription activated successfully",
                    **subscription_data
                },
                status=status.HTTP_200_OK
            )
            
        return Response(
            {
                "success": False,
                "message": "Trial activation failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def _get_trial_features(self):
        """Return features available in trial plan"""
        return [
            "basic_hostel_management",
            "student_registration",
            "room_allocation",
            "basic_reports",
            "maintenance_tracking"
        ]


# ---------------- Premium Subscription API ----------------
class PremiumSubscriptionView(APIView):
    def post(self, request):
        """Create a premium subscription for the user"""
        serializer = PremiumSubscriptionSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            payment_method = serializer.validated_data['payment_method']
            amount = serializer.validated_data['amount']
            receipt_file = serializer.validated_data.get('receipt')
            
            user = User.objects.get(user_id=user_id)
            
            # Create subscription in Subscription model
            subscription = Subscription.objects.create(
                user=user,
                account_type='premium',
                end_date=datetime.now() + timedelta(days=365),  # 1 year premium
                reciept=receipt_file if receipt_file else None  # Save receipt if provided
            )
            
            # Update user expiry date
            user.expiry_date = subscription.end_date
            user.save()
            
            # Generate subscription data from Subscription model
            subscription_data = {
                "subscription_id": str(subscription.subscription_id),
                "plan_type": "premium",
                "status": "pending_payment",
                "subscription_date": subscription.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_date": subscription.end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if subscription.end_date else None,
                "payment_method": payment_method,
                "amount": float(amount),
                "currency": "INR",
                "features": self._get_premium_features()
            }
            
            # Include receipt URL if receipt was uploaded
            if subscription.reciept:
                try:
                    # Get the URL from Cloudinary storage
                    receipt_url = subscription.reciept.url if subscription.reciept else None
                    subscription_data["receipt_url"] = receipt_url
                except Exception as e:
                    logger.error(f"Error getting receipt URL: {str(e)}")
                    subscription_data["receipt_url"] = str(subscription.reciept) if subscription.reciept else None
            
            return Response(
                {
                    "success": True,
                    "message": "Premium subscription created successfully",
                    **subscription_data
                },
                status=status.HTTP_200_OK
            )
            
        return Response(
            {
                "success": False,
                "message": "Premium subscription creation failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def _get_premium_features(self):
        """Return features available in premium plan"""
        return [
            "advanced_hostel_management",
            "unlimited_students",
            "advanced_analytics",
            "custom_reports",
            "priority_support",
            "inventory_management",
            "expense_tracking",
            "mess_management"
        ]


# ---------------- Payment Detail API ----------------
class PaymentDetailView(APIView):
    def get(self, request):
        """Get payment details for premium subscription"""
        # Generate a sample QR code (1x1 pixel PNG)
        # In production, you would generate a proper QR code with payment details
        qr_code_data = "https://res.cloudinary.com/day4qwoi9/image/upload/v1762425353/qrcode_fc9npg.png"
        
        # Calculate valid until date (24 hours from now)
        from datetime import datetime, timedelta
        valid_until = datetime.now() + timedelta(hours=24)
        
        response_data = {
            "success": True,
            "amount": 19999,
            "currency": "INR",
            "qr_code": qr_code_data,
            "upi_id": "prajwalynx@idfcbank",
            "payment_description": "HostelApp Premium Subscription - Annual Plan",
            "valid_until": valid_until.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    

# ---------------- Receipt Upload API ----------------

class ReceiptUploadView(APIView):
    def post(self, request, subscription_id):
        """Upload receipt image for a subscription"""
        serializer = ReceiptUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            receipt_file = serializer.validated_data['receipt']
            
            response_data = {
                "success": True,
                "message": "Receipt uploaded successfully",
                "subscription_id": subscription_id,
                "file_name": receipt_file.name,
                "file_size": receipt_file.size,
                "file_type": receipt_file.content_type
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        return Response(
            {
                "success": False,
                "message": "Receipt upload failed",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ---------------- User Subscription Details API ----------------
class UserSubscriptionView(APIView):
    def get(self, request, user_id):
        """Get subscription details for a specific user"""
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "User not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get the latest subscription from Subscription model
        subscription = Subscription.objects.filter(user=user).order_by('-created_at').first()
        
        if subscription:
            # Generate subscription data based on subscription's account type
            if subscription.account_type == "free_trial":
                subscription_data = {
                    "success": True,
                    "subscription_id": str(subscription.subscription_id),
                    "plan_type": "trial",
                    "status": "active" if subscription.end_date and subscription.end_date.date() > date.today() else "expired",
                    "subscription_date": subscription.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end_date": subscription.end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if subscription.end_date else None,
                    "days_remaining": (subscription.end_date.date() - date.today()).days if subscription.end_date and subscription.end_date > date.today() else 0,
                    "features": self._get_trial_features()
                }
            elif subscription.account_type == "premium":
                subscription_data = {
                    "success": True,
                    "subscription_id": str(subscription.subscription_id),
                    "plan_type": "premium",
                    "status": "active" if subscription.end_date and subscription.end_date.date() > date.today() else "expired",
                    "payment_status": "paid",
                    "payment_method": "upi",
                    "amount": 19999,
                    "currency": "INR",
                    "subscription_date": subscription.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end_date": subscription.end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if subscription.end_date else None,
                    "receipt_url": f"https://storage.example.com/receipts/receipt_{str(subscription.subscription_id)[:8]}.jpg",
                    "features": self._get_premium_features()
                }
            else:
                # Default case for unknown account types
                subscription_data = {
                    "success": True,
                    "subscription_id": str(subscription.subscription_id),
                    "plan_type": "basic",
                    "status": "active" if subscription.end_date and subscription.end_date.date() > date.today() else "expired",
                    "subscription_date": subscription.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end_date": subscription.end_date.strftime("%Y-%m-%dT%H:%M:%SZ") if subscription.end_date else None,
                    "days_remaining": (subscription.end_date.date() - date.today()).days if subscription.end_date and subscription.end_date > date.today() else 0,
                    "features": self._get_basic_features()
                }
        else:
            # No subscription found
            subscription_data = {
                "success": True,
                "subscription_id": None,
                "plan_type": "basic",
                "status": "no_subscription",
                "subscription_date": None,
                "end_date": None,
                "days_remaining": 0,
                "features": self._get_basic_features()
            }
        
        return Response(subscription_data, status=status.HTTP_200_OK)
    
    def _get_trial_features(self):
        """Return features available in trial plan"""
        return [
            "basic_hostel_management",
            "student_registration",
            "room_allocation",
            "basic_reports",
            "maintenance_tracking"
        ]
    
    def _get_premium_features(self):
        """Return features available in premium plan"""
        return [
            "advanced_hostel_management",
            "unlimited_students",
            "advanced_analytics",
            "custom_reports",
            "priority_support",
            "inventory_management",
            "expense_tracking",
            "mess_management"
        ]
    
    def _get_basic_features(self):
        """Return features available in basic plan"""
        return [
            "basic_hostel_management",
            "student_registration",
            "room_allocation"
        ]
