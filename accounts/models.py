from django.db import models
from authentication.models import User, Drivers
from bookings.models import Bookings
import uuid
from django.utils import timezone



class Account(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    amount = models.CharField(max_length=500, default='0.00')
    debt = models.CharField(max_length=500, default='0.00')
    latest_booking = models.OneToOneField(Bookings, on_delete=models.CASCADE, default='', blank=True, null=True)
    is_paid = models.BooleanField(default=False, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} account"
