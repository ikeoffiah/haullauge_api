from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import TrackLocation
from rest_framework.response import Response
from .serializers import TrackingSerializer
from authentication.utils import success_message_helper, system_error_message_helper



class UpdateTrackingView(APIView):
    permission_classes = [IsAuthenticated,]

    def get_object(self, pk):
        try:
            return TrackLocation.objects.get(id=pk)
        except TrackLocation.DoesNotExist:
            return Response(system_error_message_helper({'error': 'Tracking cannot be found'}),
                            status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        tracking = self.get_object(pk)
        serializer = TrackingSerializer(tracking, data=request.data, context={'request': request, 'track':tracking.booking})
        if serializer.is_valid():
            serializer.save()
            return Response(success_message_helper(serializer.data, "Success"), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status = status.HTTP_400_BAD_REQUEST)
