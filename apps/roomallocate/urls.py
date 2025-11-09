# roomallocation/urls.py
from django.urls import path
from .views import (
    AllocateBedView,
    AllocationDetailView,
    AllocationListView,
    AvailableBedsByBuildingView,
    AvailableBedsView,
    DeallocateBedView,
    GetAllocatedBedsStudentView,
    RoomStatusView,
    StudentRoomIssueByStudentView,
    StudentRoomIssueListCreateView,
    StudentRoomIssueUpdateView,
)

urlpatterns = [
    path("allocate-bed/", AllocateBedView.as_view(), name="allocate-bed"),
    path("deallocate-bed/<uuid:allocation_id>/",DeallocateBedView.as_view(),name="deallocate-bed"),
    path("allocations/", AllocationListView.as_view(), name="allocation-list"),
    path("allocations/<uuid:allocation_id>/",AllocationDetailView.as_view(),name="allocation-detail"),
    path("available-beds/", AvailableBedsView.as_view(), name="available-beds"),
    path("room-status/<uuid:room_id>/", RoomStatusView.as_view(), name="room-status"),
    path("buildings/<uuid:building_id>/available-beds/",AvailableBedsByBuildingView.as_view(),name="available-beds-building"),
    path("issues/", StudentRoomIssueListCreateView.as_view(), name="all_issues"),
    path("issues/student/<uuid:student_id>/", StudentRoomIssueByStudentView.as_view(), name="issues_by_student"),
    path("issues/<uuid:issue_id>/", StudentRoomIssueUpdateView.as_view(), name="update_issue"),
]
