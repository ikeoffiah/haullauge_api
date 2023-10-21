from django.db import models
import uuid
from bookings.models import Locations, Bookings
from .constants import TRACKING_STATUS

# Create your models here.

class TrackLocation(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    pickup_location = models.OneToOneField(Locations, on_delete=models.CASCADE, related_name="trackPickup")
    delivery_location = models.OneToOneField(Locations, on_delete=models.CASCADE, related_name="trackDelivery")
    last_location = models.OneToOneField(Locations, on_delete=models.CASCADE, related_name="trackLastLocation")
    booking = models.OneToOneField(Bookings, on_delete=models.CASCADE, related_name="trackBooking", default='')
    status = models.CharField(max_length=100, default=TRACKING_STATUS.STARTING)
    tracking_id = models.CharField(max_length=100, default='')
    is_arrived = models.BooleanField(default=False)
    is_pickedUp = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tracking {self.tracking_id}"

