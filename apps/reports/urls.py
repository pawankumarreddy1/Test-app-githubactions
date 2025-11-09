from django.urls import path
from .views import HostelRoomReportView, OccupiedBedReportView, BuildingStudentsReportView, BedReportView
 
urlpatterns = [
    path("rooms-reports/<uuid:building_id>/", HostelRoomReportView.as_view(), name="building-room-report"),
    path('beds-reports/<uuid:building_id>/', OccupiedBedReportView.as_view(), name='occupied-bed-report'),
    path('students-reports/<uuid:building_id>/', BuildingStudentsReportView.as_view(), name='building-students-report'),
    path('bed-report/', BedReportView.as_view(), name='bed-report'),
]
 