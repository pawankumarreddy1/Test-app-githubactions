# apps/fees/urls.py
from django.urls import path
from .views import CollectFeeView, FeeDashboardView

urlpatterns = [
    
    path("collect-fee/", CollectFeeView.as_view(), name="collect-fee"),
    path("collect-fee/<uuid:fee_id>/", CollectFeeView.as_view(), name="update-fee"),
    path('fee-dashboard/', FeeDashboardView.as_view(), name='fee-dashboard'),
]
