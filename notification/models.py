from django.db import models
from authentication.models import User
import uuid

class Notifications(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE,default='')
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
