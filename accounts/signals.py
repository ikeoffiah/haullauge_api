from django.db.models.signals import post_save
from django.dispatch import receiver
from authentication.models import Drivers
from .models import Account

@receiver(post_save, sender=Drivers)
def create_account(sender, instance, created, **kwargs):
    print("here--------------------")
    if created:
        Account.objects.create(
            user=instance.driver
        )

