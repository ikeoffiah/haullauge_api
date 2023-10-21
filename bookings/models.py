from django.db import models
from authentication.models import User, Drivers
import uuid
from .utils import format_string_datetime
from django.utils import timezone
from .constants import *


class Locations(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    longitude = models.FloatField()
    latitude = models.FloatField()
    name = models.CharField(max_length=500, default='')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  f"{self.name}"



class Bookings(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    reference_id = models.CharField(max_length=200, default='')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    pickup_location = models.OneToOneField(Locations, on_delete=models.CASCADE, related_name="pickup")
    delivery_location = models.OneToOneField(Locations, on_delete=models.CASCADE, related_name="delivery")
    truckType = models.CharField(max_length=500, default='')
    description = models.CharField(max_length=500, default='')
    photo_url = models.CharField(max_length=500, default='')
    instruction = models.CharField(max_length=500, default='')
    weight = models.FloatField(blank=True, null=True)
    hour = models.IntegerField(blank=True, null=True)
    mins = models.IntegerField(blank=True, null=True)
    load = models.CharField(max_length=200, default='')
    time = models.CharField(max_length=200, default='')
    date = models.CharField(max_length=200, default='')
    distance = models.CharField(max_length=100, default='')
    pickup_price = models.IntegerField()
    delivery_price = models.IntegerField()
    pickup_date = models.DateTimeField(blank=True, default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        self.pickup_date = format_string_datetime(self.date, self.time)
        super(Bookings, self).save(*args, **kwargs)


    def __str__(self):
        return self.truckType



class Hauls(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="haul")
    booking = models.OneToOneField(Bookings, on_delete=models.CASCADE)
    status = models.CharField(max_length=200, default=HAUL_STATUS.Pending)
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="driver", null=True, blank=True)
    plate_number = models.CharField(max_length=200, default='')
    arrival_time = models.CharField(max_length=200, default='')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.first_name


