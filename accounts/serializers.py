from rest_framework import serializers
from .models import Account
from authentication.models import User, Drivers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number',)

class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    driver_profile_photo = serializers.SerializerMethodField()
    class Meta:
        model = Account
        fields = ('amount', 'debt', 'user','deadline','driver_profile_photo',)

    def get_driver_profile_photo(self, obj):
        driver = Drivers.objects.get(driver=obj.user)
        profile_url = driver.profile_img
        return profile_url
