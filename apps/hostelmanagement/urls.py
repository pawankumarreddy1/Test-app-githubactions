from django.urls import path
from .views import (
    AvailableBedsView,
    BedByRoomView,
    BedDetailView,
    BedView,
    AvailableBedsView,
    BuildingByHostelView,
    BuildingDetailView,
    BuildingView,
    BulkRoomUpdateAPIView,
    Deleteinventory,
    FloorByBuildingView,
    FloorDetailView,
    FloorView,
    FloorTotalRoomsUpdateAPIView,
    HostelDetailView,
    HostelView,
    HostelByOwnerView,
    InventoryDetailsByBuildingView,
    RoomByFloorView,
    RoomDetailView,
    RoomView,
    InventoryListView,
    InventoryDetailView,
    BuildingRoomsInventoryView,
    RoomInventoryDetailView,
    BulkInventoryCreateView,
    BedAnalyticsView,
    StudentDetailsView,
)

urlpatterns = [
    #------Hostel-------
    path("hostels/", HostelView.as_view(), name="hostel-list"),
    path("hostels/<uuid:hostel_id>/", HostelDetailView.as_view(), name="hostel-detail"),
    path("hostels-by-owner/<uuid:owner_id>/", HostelByOwnerView.as_view(), name="hostel-owner-detail"),

    #------Building-----
    path("buildings/", BuildingView.as_view(), name="building-list"),
    path(
        "buildings/<uuid:building_id>/",
        BuildingDetailView.as_view(),
        name="building-detail",
    ),
    path("buildings-by-hostel/<uuid:hostel_id>/", BuildingByHostelView.as_view(), name="building-hostel-detail"),

    #------Floor------
    path("floors/", FloorView.as_view(), name="floor-list"),
    path("floors/<uuid:floor_id>/", FloorDetailView.as_view(), name="floor-detail"),
    path("floors-by-building/<uuid:building_id>/", FloorByBuildingView.as_view(), name="floor-building-detail"),

    #------Total Rooms in Floor------
    path("total-rooms-create/", FloorTotalRoomsUpdateAPIView.as_view(), name="floor-total-rooms-update"),

    #------Room-------
    path("rooms/", RoomView.as_view(), name="room-list"),
    path("rooms/<uuid:room_id>/", RoomDetailView.as_view(), name="room-detail"),
    path("rooms/bulk-update/", BulkRoomUpdateAPIView.as_view(), name="bulk-room-update"),
    path("rooms-by-floor/<uuid:floor_id>/", RoomByFloorView.as_view(), name="room-floor-detail"),
    path("rooms/inventories-delete/<uuid:room_id>", Deleteinventory.as_view(), name="delete_room_inventories"),
    #------Bed-------
    path("beds/", BedView.as_view(), name="bed-list"),
    path("beds/available/", AvailableBedsView.as_view(), name="available-bed-list"),
    path("beds/<uuid:bed_id>/", BedDetailView.as_view(), name="bed-detail"),
    path("beds-by-room/<uuid:room_id>/", BedByRoomView.as_view(), name="bed-room-detail"),
    #------Inventory-------
    path("inventories/", InventoryListView.as_view(), name="inventory-list"),  # GET all inventories
    path("inventories/<uuid:inventory_id>/", InventoryDetailView.as_view(), name="inventory-detail"),  # GET/PUT/DELETE single inventory
    path("inventories/bulk-create/", BulkInventoryCreateView.as_view(), name="inventory-bulk-create"),  # POST bulk
    path("building/<uuid:building_id>/rooms-inventories/", BuildingRoomsInventoryView.as_view(), name="building-rooms-inventories"),  # GET by building
    path("room/<uuid:room_id>/inventories/", RoomInventoryDetailView.as_view(), name="room-inventories"),  # GET/PUT by room_id
    path("students-by-building/<uuid:building_id>/", StudentDetailsView.as_view(), name="students-by-building"),
    #------Analytics-------
    path("analytics-inventory/<uuid:building_id>/", BedAnalyticsView.as_view(), name="bed-analytics"),  # GET bed analytics by building
    path("inventory-details-by-building/<uuid:building_id>/", InventoryDetailsByBuildingView.as_view(), name="inventory-details-by-building"),

]
