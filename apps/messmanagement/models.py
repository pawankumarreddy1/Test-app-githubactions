from django.db import models

class Mess(models.Model):
    building_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.building_id


class Meal(models.Model):
    mess = models.ForeignKey(Mess, related_name="meals", on_delete=models.CASCADE)
    meal = models.CharField(max_length=50)
    timing = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=[("Available", "Available"), ("Not Available", "Not Available")])
    menu = models.JSONField(default=list)  # Stores list of menu items
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.meal} ({self.mess.building_id})"
