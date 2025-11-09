from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CollectFee


@receiver(post_save, sender=CollectFee)
def update_fee_dashboard(sender, instance, created, **kwargs):
    if created:
        # Here you could update a cache or recompute summary
        print(f"✅ Fee collected for {instance.student.student_name}: ₹{instance.amount}")
