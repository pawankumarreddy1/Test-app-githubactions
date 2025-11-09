from django.urls import path
from .views import MessView

urlpatterns = [
    path('mess/<str:building_id>/', MessView.as_view(), name='mess-detail'),
    path('mess/', MessView.as_view(), name='mess-create'),
]
