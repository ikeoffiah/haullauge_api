from rest_framework import status
from rest_framework import generics
from .serializers import NotificationSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notifications
from authentication.utils import generate_send_otp, verify_otp, success_message_helper, error_message_helper, send_drivers_msg, system_error_message_helper, generateReferenceId


class GetUnreadNotificationNumber(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, ]

    def get(self,request):
        notification = Notifications.objects.filter(user= request.user, is_read=False)
        unread_notification_number = len(notification)
        return Response(success_message_helper(unread_notification_number, 'Notifications successfully fetched'),
                        status=status.HTTP_200_OK)


class GetNotifications(generics.GenericAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self,request):
        notification = Notifications.objects.filter(user=request.user).update(is_read=True)
        serializer = self.serializer_class(notification, many=True)
        return Response(success_message_helper(serializer.data, 'Notifications successfully fetched'),
                        status=status.HTTP_200_OK)



