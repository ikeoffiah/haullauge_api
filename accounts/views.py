from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import AccountSerializer
from .models import Account
from rest_framework.response import Response
from authentication.utils import success_message_helper, error_message_helper, system_error_message_helper


class GetAccountDetails(generics.GenericAPIView):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        account = Account.objects.get(user= request.user)
        serializer = self.serializer_class(account)
        return Response(success_message_helper(serializer.data, 'Account successfully fetched'),
                        status=status.HTTP_200_OK)