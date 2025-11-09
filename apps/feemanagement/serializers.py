# apps/fees/serializers.py
from rest_framework import serializers
from .models import CollectFee
from apps.hostelmanagement.models import Student


class CollectFeeSerializer(serializers.ModelSerializer):
   
    student_id = serializers.UUIDField(write_only=True)
    def validate(self, data):
        student_id = data.get("student_id")
        if student_id:
            try:
                student = Student.objects.get(pk=student_id)
                data["student"] = student
            except Student.DoesNotExist:
                raise serializers.ValidationError({"student_id": "Student not found"})
        else:
            raise serializers.ValidationError({"student_id": "Student ID is required"})
        return data
    
   
    class Meta:
        model = CollectFee
        fields = [
            "fee_id",
            "student_id",
            "payment_type",
            "amount",
            "payment_method",
            "transaction_reference",
            "remarks",
            "payment_date",
        ]
        read_only_fields = ["fee_id", "payment_date"]

    def create(self, validated_data):
        student_id = validated_data.pop("student_id")
        try:
            student = Student.objects.get(pk=student_id)
            validated_data["student"] = student
        except Student.DoesNotExist:
            raise serializers.ValidationError({"student_id": "Student not found"})
        return CollectFee.objects.create(**validated_data)
