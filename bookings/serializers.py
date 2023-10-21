from rest_framework import serializers
from .models import Bookings, Locations, Hauls
from authentication.models import User, Drivers
from tracking.models import TrackLocation



class DriverDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    driver_profile_photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number","driver_profile_photo"]

    def get_driver_profile_photo(self, obj):
        driver = Drivers.objects.get(driver=obj)
        profile_url = driver.profile_img
        return profile_url


class AssignDriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        exclude = ('id',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name','last_name','phone_number',)

class BookingSerializer(serializers.ModelSerializer):
    pickup_location = LocationSerializer()
    delivery_location = LocationSerializer()
    instruction = serializers.CharField(required=False)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Bookings
        exclude = ('id', 'reference_id','pickup_price', 'delivery_price','load')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = instance.id
        ret['reference_id'] = instance.reference_id
        ret['pickup_price'] = instance.pickup_price
        ret['delivery_price'] = instance.delivery_price
        return ret




class FileUploadSerializer(serializers.Serializer):
    image_file = serializers.FileField()


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackLocation
        exclude = ('updated_at','created_at',)

class HaulSerializer(serializers.ModelSerializer):
    booking = BookingSerializer()
    driver = DriverDetailSerializer(required=False)
    tracker = serializers.SerializerMethodField()

    class Meta:
        model = Hauls
        fields = ('booking','driver','status','arrival_time','tracker',)


    def get_tracker(self,obj):
        track = TrackLocation.objects.filter(booking=obj.booking)
        if track.exists():
            tracking = TrackSerializer(track[0])
            return tracking.data
        else:
            return {}


    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = instance.id
        ret['user_id'] = instance.user.id
        return ret

class HaulUpdateSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(required=False)
    driver = DriverDetailSerializer(required=False, read_only=True)
    class Meta:
        model = Hauls
        exclude = ('id','user',)


class AcceptHaulSerializer(serializers.Serializer):
    longitude = serializers.FloatField(required=True)
    latitude = serializers.FloatField(required=True)
    distance = serializers.CharField(required=True)
    time = serializers.CharField(required=True)
    duration = serializers.CharField(required=True)
    location_name = serializers.CharField(required=True)
