from rest_framework import serializers
from .models import TrackLocation
from .constants import TRACKING_STATUS_CHOICES, TRACKING_STATUS
from bookings.utils import send_push_notification
from bookings.models import Hauls
from bookings.constants import HAUL_STATUS



class TrackingSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices= TRACKING_STATUS_CHOICES)

    def get_fields(self):
        fields = super().get_fields()
        for field_name, field in fields.items():
            field.required = False
        return fields

    class Meta:
        model = TrackLocation
        exclude = ("created_at", "updated_at",)


    def validate(self, attrs):
        status = attrs.get("status", None)
        request = self.context.get('request')
        track = self.context.get('track')
        user = request.user
        print(user)
        print(status)
        if status is not None:
            if status == TRACKING_STATUS.PICKUP:
                haul = Hauls.objects.get(booking=track)
                send_push_notification(haul.user.id,f"Your driver,{haul.driver.first_name} {haul.driver.last_name}, has arrived at pick up location", "Truck arrived")
            if status == TRACKING_STATUS.DELIVERY:
                haul = Hauls.objects.get(booking=track)
                send_push_notification(haul.user.id,f"Your driver ,{haul.driver.first_name} {haul.driver.last_name}, has arrived at delivery location", "Load delivered")

                haul.status = HAUL_STATUS.Delivered
                haul.save()
        else:
            return attrs
        return attrs