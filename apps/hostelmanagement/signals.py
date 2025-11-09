from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Bed, Building, Floor, Room


@receiver(post_save, sender=Building)
def create_floors(sender, instance, created, **kwargs):
    if created:
        for i in range(instance.total_floors):
            Floor.objects.create(
                building=instance,
                floor_number=i + 1,
            )


@receiver(pre_save, sender=Floor)
def create_rooms_based_on_total_rooms(sender, instance, **kwargs):
    """
    Automatically create rooms when total_rooms is increased
    This signal will be triggered before saving the Floor instance
    """
    if instance.pk:  # Only for existing floors (not new ones)
        try:
            old_instance = Floor.objects.get(pk=instance.pk)
            old_total_rooms = old_instance.total_rooms or 0
            new_total_rooms = instance.total_rooms or 0
            
            # Only create rooms if total_rooms is being increased
            if new_total_rooms > old_total_rooms:
                current_room_count = old_instance.rooms.count()
                rooms_to_create = new_total_rooms - current_room_count
                
                # Create the additional rooms
                for i in range(rooms_to_create):
                    room_number = ""
                    
                    Room.objects.create(
                        floor=instance,
                        room_number=room_number,
                        room_type="NON_AC",  
                        monthly_rent="",   
                        total_beds="",
                        is_available=True
                    )
        except Floor.DoesNotExist:
            # Floor doesn't exist yet, skip room creation
            pass


@receiver(post_save, sender=Room)
def sync_beds_with_total_beds(sender, instance, created, **kwargs):
    """
    Create beds automatically only if none exist yet for the room.
    - If the room already has beds, leave them unchanged regardless of total_beds updates.
    - If there are no beds and total_beds > 0, create exactly total_beds beds.
    """
    try:
        total_beds = int(instance.total_beds) if instance.total_beds else 0
    except ValueError:
        total_beds = 0  # fallback if total_beds is not a valid integer

    current_beds_count = instance.beds.count()

    # Only create beds if none exist yet
    if current_beds_count == 0 and total_beds > 0:
        for index in range(1, total_beds + 1):
            Bed.objects.create(
                room=instance,
                bed_number=str(index),
            )

    # Update room availability flag based on any unoccupied bed
    instance.is_available = instance.beds.filter(is_occupied=False).exists()
    # Save only the availability field to avoid re-triggering unnecessary changes
    Room.objects.filter(pk=instance.pk).update(is_available=instance.is_available)
