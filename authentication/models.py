from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone




class CustomUserManager(BaseUserManager):
    """Authentication for User"""
    def create_user(self, email,phone_number, first_name, last_name,password, **extra_fields):
        if not phone_number:
            raise ValueError(_("phone number must be set"))

        if email:
            email = self.normalize_email(email)


        user = self.model(phone_number=phone_number, email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user_without_email(self, phone_number, first_name, last_name,password, **extra_fields):
        if not phone_number:
            raise ValueError(_("phone number must be set"))

        user = self.model(phone_number=phone_number, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user


    def create_superuser(self,email, phone_number, first_name, last_name,password, **extra_fields):
        """Authentication for superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser is_staff must be True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user( email=email,phone_number=phone_number,first_name=first_name, last_name=last_name,password=password, **extra_fields )


class User(AbstractBaseUser, PermissionsMixin):
    """User model authentication for all type of user authentications"""
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    phone_number = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True,null=True, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length= 200)
    pics = models.CharField(max_length=200, default='')
    is_staff = models.BooleanField(default=False)
    user_kind = models.CharField(max_length=100, default='user')
    device_token = models.CharField(max_length=1000, default='')
    is_active = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


    def tokens(self):
        refresh_token = RefreshToken.for_user(self)
        return {
            'refresh':str(refresh_token),
            'access':str(refresh_token.access_token)
        }




class Agents(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    special_id = models.CharField(max_length=100, default='')
    verification_photo = models.CharField(max_length=500)
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent.first_name} {self.agent.last_name} (Agent)"



class Drivers(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4)
    driver = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agents, on_delete=models.CASCADE)
    truck = models.CharField(max_length=100, default='')
    document = models.CharField(max_length=500, default='')
    profile_img = models.CharField(max_length=500, default='')
    driving_licence = models.CharField(max_length=500, default='')
    insurance_doc = models.CharField(max_length=500, default='')
    vehicle_doc = models.CharField(max_length=500, default='')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.driver.first_name} (driver) of {self.agent.agent.first_name} {self.agent.agent.last_name} (agent)"


