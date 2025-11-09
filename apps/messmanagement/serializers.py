from rest_framework import serializers
from .models import Mess, Meal

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'meal', 'timing', 'status', 'menu', 'created_at', 'updated_at']


class MessSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True)

    class Meta:
        model = Mess
        fields = ['building_id', 'meals']

    def create(self, validated_data):
        meals_data = validated_data.pop('meals')
        mess = Mess.objects.create(**validated_data)
        for meal_data in meals_data:
            Meal.objects.create(mess=mess, **meal_data)
        return mess

    def update(self, instance, validated_data):
        meals_data = validated_data.pop('meals', [])
        instance.building_id = validated_data.get('building_id', instance.building_id)
        instance.save()

        # Clear existing meals and recreate
        instance.meals.all().delete()
        for meal_data in meals_data:
            Meal.objects.create(mess=instance, **meal_data)
        return instance
