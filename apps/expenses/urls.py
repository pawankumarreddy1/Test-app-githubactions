from django.urls import path
from .views import (
    ExpenseCreateAPIView,
    ExpenseByBuildingAPIView,
    ExpenseUpdateAPIView,
    ExpenseDeleteAPIView,
)

urlpatterns = [
    path("expenses/<uuid:building_id>/create/", ExpenseCreateAPIView.as_view(), name="create_expense"),
    path("expenses/<uuid:building_id>/", ExpenseByBuildingAPIView.as_view(), name="list_expenses"),
    path("expenses/update/", ExpenseUpdateAPIView.as_view(), name="update_expense"),
    path("expenses/delete/", ExpenseDeleteAPIView.as_view(), name="delete_expense"),
]
