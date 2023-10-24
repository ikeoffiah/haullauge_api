from django.utils import timezone
from django.db.models import F
from .constants import *
from .models import Bookings, Locations, Hauls
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import BookingSerializer, HaulSerializer, FileUploadSerializer, HaulUpdateSerializer,AcceptHaulSerializer
from rest_framework.response import Response
from accounts.utils import create_account
from authentication.utils import generate_send_otp, verify_otp, success_message_helper, error_message_helper, send_drivers_msg, system_error_message_helper, generateReferenceId
from .utils import calculatePrice, send_push_notification
from authentication.models import User, Drivers
import cloudinary
from django.http import Http404
from rest_framework.views import APIView
from .utils import format_string_datetime
from tracking.utils import create_track


class BookingView(generics.GenericAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():

            distance = serializer.validated_data['distance']
            weight = serializer.validated_data['weight']
            fuel_price = 12
            price = calculatePrice(float(distance),weight, fuel_price)

            serializer.validated_data['user'] = request.user
            serializer.validated_data['delivery_price'] = price
            serializer.validated_data['pickup_price'] = price
            serializer.validated_data['reference_id'] = price

            serializer.validated_data["pickup_location"] = Locations.objects.create(
                **serializer.validated_data["pickup_location"])
            serializer.validated_data["delivery_location"] = Locations.objects.create(
                **serializer.validated_data["delivery_location"])

            serializer.save()
            return Response(success_message_helper(serializer.data, "Booking was successful"), status= status.HTTP_200_OK)

        return Response(system_error_message_helper(serializer.errors), status = status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        booking = Bookings.objects.filter(user= request.user)
        serializer = self.serializer_class(booking, many=True)
        return Response(success_message_helper(serializer.data, 'Bookings successfully fetched'), status= status.HTTP_200_OK)


class AcceptHaulView(APIView):
    permission_classes = [IsAuthenticated, ]


    def get_object(self, pk):
        try:
            return Bookings.objects.get(id=pk)
        except Bookings.DoesNotExist:
            return Response(system_error_message_helper({'error': 'Booking does not exist'}),
                            status=status.HTTP_404_NOT_FOUND)


    def put(self, request, pk):
        booking = self.get_object(pk)
        haul_filter = Hauls.objects.filter(booking=booking)
        haul = haul_filter[0]

        if haul.status == HAUL_STATUS.Cancelled:
            return Response(system_error_message_helper({'error': 'Haul has been cancelled'}),
                            status=status.HTTP_400_BAD_REQUEST)

        if haul.driver:
            if haul.driver == request.user:
                return Response(system_error_message_helper({'error': 'This haul has been accepted by you'}),
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(system_error_message_helper({'error': 'Haul has been assigned to another driver'}),
                            status=status.HTTP_400_BAD_REQUEST)
        input_serializer = AcceptHaulSerializer(data=request.data)
        date = timezone.now()
        # serializer.validated_data
        if input_serializer.is_valid():
            log = input_serializer.validated_data['longitude']
            lat = input_serializer.validated_data['latitude']
            distance = input_serializer.validated_data['distance']
            time = input_serializer.validated_data['time']
            duration = input_serializer.validated_data['duration']
            location_name = input_serializer.validated_data['location_name']
            pickup = booking.pickup_location
            delivery = booking.delivery_location


        else:
            return Response(system_error_message_helper(input_serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        driver = User.objects.filter(id=request.user.id, user_kind="driver")
        is_driver = Drivers.objects.filter(driver=driver[0]).exists()
        if not is_driver:
            return Response(system_error_message_helper({'error': 'Driver not found.'}),
                            status=status.HTTP_400_BAD_REQUEST)
        haul.driver = driver[0]
        haul.status = HAUL_STATUS.InProcess
        haul.save()
        # send notification if a driver is assigned to a haul
        print("Send Notification")
        user_id = haul.user.id
        driver_first_name = request.user.first_name
        driver_last_name = request.user.last_name
        send_push_notification(user_id,f"{driver_first_name} {driver_last_name} (Driver) accepted your haul", "Haul accepted")
        pickUp_price = booking.pickup_price
        delivery_price = booking.delivery_price
        create_account(request.user.id, pickUp_price, delivery_price, booking)
        create_track(pickup, delivery, log, lat, distance, time, duration, date, location_name, booking)
        serializer = HaulUpdateSerializer(haul)
        if serializer:
            return Response(success_message_helper(serializer.data, "Success"), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status = status.HTTP_400_BAD_REQUEST)



class HaulUpdateView(APIView):
    permission_classes = [IsAuthenticated,]

    def get_object(self, pk):
        try:
            return Bookings.objects.get(id=pk)
        except Bookings.DoesNotExist:
            return Response(system_error_message_helper({'error': 'Booking does not exist'}),
                            status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        booking = self.get_object(pk)
        haul_filter = Hauls.objects.filter(booking=booking)
        haul = haul_filter[0]

        if haul.status == HAUL_STATUS.Cancelled:
            return Response(system_error_message_helper({'error': 'Haul has been cancelled'}),
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = HaulUpdateSerializer(haul, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(success_message_helper(serializer.data, "Success"), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status = status.HTTP_400_BAD_REQUEST)



class HaulsView(generics.GenericAPIView):
    serializer_class = HaulSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        hauls = Hauls.objects.filter(user= request.user).order_by('-updated_at')
        serializer = self.serializer_class(hauls, many=True)
        return Response(success_message_helper(serializer.data, 'Hauls successfully fetched'),
                        status=status.HTTP_200_OK)


class GetHaulByStatus(generics.GenericAPIView):
    serializer_class =  HaulSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        quaryparam = request.GET
        query_status = quaryparam.get('status')

        if query_status:

            hauls = Hauls.objects.filter(status=query_status, user= request.user).order_by('-updated_at')
            serializer = self.serializer_class(hauls, many=True)
            return Response(success_message_helper(serializer.data, 'Hauls successfully fetched'), status= status.HTTP_200_OK)
        return Response(error_message_helper("", 'Query provided is wrong'), status=status.HTTP_406_NOT_ACCEPTABLE)


class UploadImageFile(generics.GenericAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            uploaded_file = cloudinary.uploader.upload(serializer.validated_data['image_file'])
            return Response(success_message_helper(uploaded_file['url'],'Image file successfully converted to url'), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status= status.HTTP_400_BAD_REQUEST)




class GetAllHaulsView(generics.GenericAPIView):
    serializer_class = HaulSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):

        hauls = Hauls.objects.filter(status=HAUL_STATUS.Pending).order_by('-updated_at')
        serializer = self.serializer_class(hauls, many=True)
        return Response(success_message_helper(serializer.data, 'Hauls successfully fetched'),
                        status=status.HTTP_200_OK)


class FilterHaul(generics.GenericAPIView):
    serializer_class =  HaulSerializer
    permission_classes = [IsAuthenticated,]

    def get(self, request):
        quaryparam = request.GET
        query_pickup_date = quaryparam.get('pickup_date')
        query_price = quaryparam.get('pickup_price')

        if query_pickup_date:

            hauls = Hauls.objects.filter(status=HAUL_STATUS.Pending).annotate(booking_pickup_date=F('booking__pickup_date')).order_by('-booking_pickup_date')
            serializer = self.serializer_class(hauls, many=True)
            return Response(success_message_helper(serializer.data, 'Hauls successfully fetched'),
                            status=status.HTTP_200_OK)

        if query_price:

            hauls = Hauls.objects.filter(status=HAUL_STATUS.Pending).annotate(booking_pickup_price=F('booking__pickup_price')).order_by('-booking_pickup_price')
            serializer = self.serializer_class(hauls, many=True)
            return Response(success_message_helper(serializer.data, 'Hauls successfully fetched'),
                            status=status.HTTP_200_OK)

        return Response(error_message_helper("",'Query provided is wrong'), status= status.HTTP_406_NOT_ACCEPTABLE)


class GetDriverHauls(generics.GenericAPIView):
    serializer_class = HaulSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        quaryparam = request.GET
        schedule = quaryparam.get('schedule')
        history = quaryparam.get('history')
        user = request.user

        if schedule:
            hauls = Hauls.objects.filter(driver=user, status= HAUL_STATUS.InProcess).order_by('-created_at')
            serializer = self.serializer_class(hauls, many=True)
            return Response(success_message_helper(serializer.data, 'Hauls successfully fetched'),
                            status=status.HTTP_200_OK)

        if history:
            hauls = Hauls.objects.filter(driver=user)
            serializer = self.serializer_class(hauls, many=True)
            return Response(success_message_helper(serializer.data, 'Hauls successfully fetched'),
                            status=status.HTTP_200_OK)

        return Response(error_message_helper("", 'Query provided is wrong'), status=status.HTTP_406_NOT_ACCEPTABLE)
