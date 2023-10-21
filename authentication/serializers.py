from rest_framework import serializers
from .models import User, Agents, Drivers
from .utils import authenticate_user_with_password, active_user_verification, get_user_token, upload_to_cloudinary
import cloudinary.uploader
from .constants import *
from .utils import system_error_message_helper



class RegisterSerializer(serializers.ModelSerializer):
    tokens = serializers.CharField(max_length=100, min_length=6, read_only=True)
    password = serializers.CharField(write_only=True, max_length=100, min_length=4, required=True)

    class Meta:
        model = User
        fields = ['phone_number','first_name','user_kind', 'last_name', 'password','tokens', 'device_token']

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError('User with this phone number already exists')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user_without_email(
            phone_number=validated_data['phone_number'],
            user_kind = validated_data['user_kind'],
            first_name= validated_data['first_name'],
            last_name=validated_data['last_name'],
            password= validated_data['password'],
            device_token = validated_data['device_token']
        )
        user.save()
        return user

class OTPVerificationSerializer(serializers.Serializer):
    secret = serializers.CharField()
    otp = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(required=False, allow_blank=True)


class LoginSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=100, required=True)
    tokens = serializers.CharField(max_length=100, min_length=6, read_only=True)
    password = serializers.CharField(write_only=True, max_length=100, min_length=4, required=True)
    device_token = serializers.CharField(max_length=1000, required=True)
    class Meta:
        model = User
        fields = ['phone_number', 'tokens', 'password', 'device_token']


    def validate(self, attrs):
        phone_number = attrs.get('phone_number', None)
        password = attrs.get('password', None)
        device_token = attrs.get('device_token',None)

        if not User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError('Phone number or Password is invalid')

        user = User.objects.get(phone_number=phone_number)

        if not authenticate_user_with_password(phone_number, password, device_token):
            raise serializers.ValidationError('Phone number or Password is invalid')

        if not active_user_verification(phone_number):
            raise serializers.ValidationError("You hasn't verified phone number")



        return {
            'token':get_user_token(phone_number),
            'phone_number':phone_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }



class RegisterDriverSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()


    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number","device_token"]

    def validate(self, attrs):
        phone_number = attrs.get("phone_number", None)

        if User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError('User with this phone number already exists')
        return attrs

    def create(self, validated_data):
        first_name = validated_data["first_name"]
        last_name = validated_data["last_name"]
        device_token = validated_data["device_token"]
        user = User.objects.create_user_without_email(first_name= validated_data['first_name'], last_name= validated_data['last_name'],phone_number= validated_data["phone_number"], password= f"{first_name}_{last_name}", user_kind='driver', device_token=device_token)
        user.save()
        return user




class DriverRegistarSerializer(serializers.Serializer):
    drivers = serializers.ListField(child= RegisterDriverSerializer())

    def create(self, validated_data):
        drivers_data = validated_data['drivers']
        drivers = []
        request = self.context.get('request')
        agent = Agents.objects.get(agent=request.user)


        for driver_data in drivers_data:
            driver_serializer = RegisterDriverSerializer(data=driver_data)
            if driver_serializer.is_valid():
                driver = driver_serializer.save()
                Drivers.objects.create(agent= agent, driver=driver)
                drivers.append(driver)

        return drivers



class AgentVerification(serializers.ModelSerializer):
    agent = serializers.PrimaryKeyRelatedField(queryset= User.objects.all())
    verification_photo = serializers.FileField()
    class Meta:
        model = Agents
        fields = ('agent', 'verification_photo')

    def create(self, validated_data):
        photo = validated_data.pop('verification_photo', None)

        if photo:
            upload_result = cloudinary.uploader.upload(photo)
            validated_data['verification_photo'] = upload_result['secure_url']

        return super().create(validated_data)


"""
This serializer would handle completing drivers registration without requiring the agents, with going through the Agent
"""
class SingleDriverRegistrationSerializer(serializers.ModelSerializer):
    document = serializers.FileField()
    profile_img = serializers.FileField()
    driving_licence = serializers.FileField()
    insurance_doc = serializers.FileField()
    vehicle_doc = serializers.FileField()
    truck = serializers.ChoiceField(choices= TRUCK_TYPE)
    agent_id = serializers.CharField()

    class Meta:
        model = Drivers
        fields = ('document','profile_img','driving_licence', 'insurance_doc', 'vehicle_doc', 'truck', 'agent_id')


    def validate(self, attrs):
        # driver = attrs.get("driver",None)

        request = self.context.get('request')
        print(request.user.user_kind)
        if request.user.user_kind != 'driver':
            raise serializers.ValidationError("You were not registered as a driver")

        driver_profile = Drivers.objects.filter(driver=request.user)

        if driver_profile.exists():
            raise serializers.ValidationError("Driver already completed registration")


        return attrs


    def create(self, validated_data):
        # document refers to ghana card
        document = validated_data.pop('document',None)
        profile_img = validated_data.pop('profile_img', None)
        driving_licence = validated_data.pop('driving_licence', None)
        insurance_doc = validated_data.pop('insurance_doc', None)
        vehicle_doc = validated_data.pop('vehicle_doc', None) #this would be the form C of the vehicle
        special_id = validated_data.pop('agent_id', None)
        request = self.context.get('request')



        validated_data['driver'] = request.user

        agent = Agents.objects.filter(special_id=special_id)

        if not agent.exists():
            raise serializers.ValidationError(system_error_message_helper({'error': 'Agent Id is invalid'}))

        validated_data['agent'] = agent[0]

        if document:
            photo_url = upload_to_cloudinary(document)
            validated_data["document"] = photo_url
        else:
            raise serializers.ValidationError(system_error_message_helper({'error': 'Ghana card must be provided'}))


        if profile_img:
            photo_url = upload_to_cloudinary(profile_img)
            validated_data["profile_img"] = photo_url
        else:
            raise serializers.ValidationError(system_error_message_helper({'error': 'Profile photo must be provided'}))


        if driving_licence:
            photo_url = upload_to_cloudinary(driving_licence)
            validated_data["driving_licence"] = photo_url
        else:
            raise serializers.ValidationError(system_error_message_helper({'error': 'Driving license must be provided'}))


        if insurance_doc:
            photo_url = upload_to_cloudinary(insurance_doc)
            validated_data["insurance_doc"] = photo_url
        else:
            raise serializers.ValidationError(
                system_error_message_helper({'error': 'Insurance must be provided'}))


        if vehicle_doc:
            photo_url = upload_to_cloudinary(vehicle_doc)
            validated_data["vehicle_doc"] = photo_url
        else:
            raise serializers.ValidationError(
                system_error_message_helper({'error': 'Form C must be provided'}))

        return super().create(validated_data)



    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['document'] = instance.document
        ret['profile_img'] = instance.profile_img
        ret['driving_licence'] = instance.driving_licence
        ret['insurance_doc'] = instance.insurance_doc
        ret['vehicle_doc'] = instance.vehicle_doc
        return ret




class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


    def validate(self, attrs):
        phone_number = attrs.get("phone_number", None)


        if not User.objects.filter(phone_number = phone_number).exists():
            raise serializers.ValidationError("User does not exist")


        return attrs


class ResendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class UpdateNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


