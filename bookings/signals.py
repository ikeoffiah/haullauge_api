from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Bookings, Hauls


@receiver(post_save, sender=Bookings)
def create_haul(sender, instance, created, **kwargs):
    if created:
        Hauls.objects.create(user=instance.user, booking=instance)