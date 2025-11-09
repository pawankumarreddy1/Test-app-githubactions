from datetime import timedelta
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import serializers

from apps.feemanagement.models import CollectFee
from .models import User, Subscription

from apps.hostelmanagement.models import Bed, Student


# ---------------- User Serializer ----------------
class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
            "email": {"required": True},
        }

   

    def validate_email(self, value):
        """
        Check if the email is already registered.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User already registered with this email. Please login."
            )
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data.pop("confirm_password", None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "password" in validated_data:
            if validated_data["password"] != validated_data.get("confirm_password"):
                raise serializers.ValidationError({"password": "Passwords do not match"})
            validated_data["password"] = make_password(validated_data["password"])
            validated_data.pop("confirm_password", None)
        return super().update(instance, validated_data)


# ---------------- Subscription Serializer ----------------
class SubscriptionSerializer(serializers.ModelSerializer):
    subscription_date = serializers.DateTimeField(source='start_date', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Subscription
        fields = [
            'subscription_id',
            'user',
            'user_email',
            'user_name',
            'account_type',
            'subscription_date',
            'start_date',
            'end_date',
            'created_at'
        ]
        read_only_fields = ['subscription_id', 'created_at', 'start_date']


# ---------------- User Registration Serializer ----------------
class UserRegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
            "email": {"required": True},
        }

    def validate_email(self, value):
        """
        Check if the email is already registered.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User already registered with this email. Please login."
            )
        return value

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data.pop("confirm_password", None)
        return super().create(validated_data)


# ---------------- User Login Serializer ----------------
class UserLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        phone = data.get("phone")
        password = data.get("password")

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid phone or password")
            
        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid phone or password")

        data["user"] = user
        return data


# ---------------- Forgot Password Serializer ----------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

class StudentdetailsSerializer(serializers.ModelSerializer):
    allocation = serializers.SerializerMethodField(read_only=True)
    payment_due = serializers.SerializerMethodField(read_only=True)
    allocated_bed = serializers.UUIDField(write_only=True)

    class Meta:
        model = Student
        fields = [
            'allocation', 'payment_due', 'allocated_bed',
            'owner', 'student_name', 'mobile_number', 'aadhar_number',
            'address', 'date_of_birth', 'emergency_name', 'emergency_phone'
        ]

    def create(self, validated_data):
        bed_id = validated_data.pop('allocated_bed')
        bed = Bed.objects.get(bed_id=bed_id)
        validated_data['allocated_bed'] = bed
        student = Student.objects.create(**validated_data)
        return student

    def update(self, instance, validated_data):
        # Handle allocated_bed update safely
        bed_id = validated_data.pop('allocated_bed', None)
        if bed_id:
            bed = Bed.objects.get(bed_id=bed_id)
            instance.allocated_bed = bed

        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_allocation(self, obj):
        bed = obj.allocated_bed
        room = bed.room if bed else None
        return {
            "allocation_id": str(bed.bed_id) if bed else None,
            "student_id": str(obj.student_id),
            "bed_id": str(bed.bed_id) if bed else None,
            "room_number": room.room_number if room else None,
            "bed_number": bed.bed_number if bed else None,
            "floor_number": room.floor.floor_number if room else None,
            "monthly_rent": str(room.monthly_rent) if room else None,
            "allocation_date": obj.created_at.date(),
            "status": "active",
            "payment_status": "pending"
        }

    def get_payment_due(self, obj):
        room_rent = obj.allocated_bed.room.monthly_rent if obj.allocated_bed else 0
        return {
            "amount_due": str(room_rent),
            "due_date": (obj.created_at + timedelta(days=7)).date() if obj.created_at else None,
            "advance_required": "5000"
        }


# ---------------- Trial Activation Serializer ----------------
class TrialActivationSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    
    def validate_user_id(self, value):
        """Validate that the user exists"""
        try:
            user = User.objects.get(user_id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
    
    def validate(self, data):
        """Additional validation for trial activation"""
        user_id = data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
            
            # Check if user already has an active trial subscription
            from datetime import datetime
            active_trial = Subscription.objects.filter(
                user=user, 
                account_type='free_trial',
                end_date__gt=datetime.now()
            ).exists()
            
            if active_trial:
                raise serializers.ValidationError("User already has an active trial subscription")
                
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
            
        return data


class CollectFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectFee
        fields = [
            'fee_id',
            'payment_type',
            'amount',
            'payment_method',
            'transaction_reference',
            'remarks',
            'payment_date'
        ]
        
class StudentListSerializer(serializers.ModelSerializer):
    payments = CollectFeeSerializer(many=True, read_only=True, source='fees')
    class Meta:
        model = Student
        fields = [
            'student_id',
            'student_name',
            'mobile_number',
            'allocated_bed', 
            'aadhar_number',
            'address',
            'date_of_birth',
            'emergency_name',
            'emergency_phone',
            'payments',
        ]


# ---------------- Premium Subscription Serializer ----------------
class PremiumSubscriptionSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    payment_method = serializers.ChoiceField(
        choices=['upi', 'card', 'netbanking', 'wallet'],
        required=True
    )
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    receipt = serializers.ImageField(required=False, allow_null=True)
    
    def validate_user_id(self, value):
        """Validate that the user exists"""
        try:
            user = User.objects.get(user_id=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
    
    def validate_amount(self, value):
        """Validate the subscription amount"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def validate_receipt(self, value):
        """Validate the uploaded receipt image"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("File size cannot exceed 5MB")
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Only JPEG, PNG, and GIF images are allowed")
        
        return value
    
    def validate(self, data):
        """Additional validation for premium subscription"""
        user_id = data.get('user_id')
        try:
            user = User.objects.get(user_id=user_id)
            
            # Check if user already has an active premium subscription
            from datetime import datetime
            active_premium = Subscription.objects.filter(
                user=user, 
                account_type='premium',
                end_date__gt=datetime.now()
            ).exists()
            
            if active_premium:
                raise serializers.ValidationError("User already has an active premium subscription")
                
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
            
        return data


# ---------------- Receipt Upload Serializer ----------------
class ReceiptUploadSerializer(serializers.Serializer):
    receipt = serializers.ImageField(required=True)
    
    def validate_receipt(self, value):
        """Validate the uploaded receipt image"""
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 5MB")
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Only JPEG, PNG, and GIF images are allowed")
        
        return value