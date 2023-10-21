from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .serializers import *
from .utils import generate_send_otp, verify_otp, success_message_helper, error_message_helper, send_drivers_msg, system_error_message_helper
from .models import User, Agents
from rest_framework.permissions import IsAuthenticated

class RegistrationView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data= data)
        if serializer.is_valid():
            serializer.save()
            serializer.validated_data['token'] = eval(serializer.data['tokens'])
            result = generate_send_otp(serializer.data['phone_number'])
            serializer.validated_data['secret'] = result['secret']
            del serializer.validated_data['password']
            return Response(success_message_helper(serializer.validated_data, "Sign Up was successful, verify your account"), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            result = generate_send_otp(serializer.data['phone_number'])
            serializer.validated_data["secret"] = result['secret']
            return Response(success_message_helper(serializer.validated_data,"Change password request successful "), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status= status.HTTP_400_BAD_REQUEST)


class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            result = generate_send_otp(serializer.data['phone_number'])
            serializer.validated_data["secret"] = result['secret']
            return Response(success_message_helper(serializer.validated_data, "OTP resent successfully"),
                            status=status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            secret = serializer.data["secret"]
            otp = serializer.data["otp"]
            phone_number = serializer.data['phone_number']
            is_verified = verify_otp(secret,otp)
            if is_verified:
                if not User.objects.filter(phone_number=phone_number).exists():
                    return Response(system_error_message_helper({'error': 'User does not exist'}),
                                    status=status.HTTP_400_BAD_REQUEST)
                user = User.objects.get(phone_number=phone_number)
                user.is_active = True
                user.save()
                return Response(success_message_helper("",'User is verified successfully'), status= status.HTTP_200_OK)
            return Response(error_message_helper("",'Verification for User failed'), status= status.HTTP_406_NOT_ACCEPTABLE)

        return Response(system_error_message_helper(serializer.errors), status= status.HTTP_400_BAD_REQUEST)


class CompletePasswordChange(generics.GenericAPIView):
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            secret = serializer.data["secret"]
            otp = serializer.data["otp"]
            phone_number = serializer.data['phone_number']
            password = serializer.data["password"]
            is_verified = verify_otp(secret, otp)
            if is_verified:
                user = User.objects.get(phone_number=phone_number)
                user.set_password(password)
                user.save()
                return Response(success_message_helper("","Password successfully changed"), status= status.HTTP_200_OK)
            return Response(error_message_helper("","Verification failed, please try again"), status= status.HTTP_400_BAD_REQUEST)
        return Response(system_error_message_helper(serializer.errors), status= status.HTTP_400_BAD_REQUEST)




class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data= data)

        if serializer.is_valid():
            return Response(success_message_helper(serializer.validated_data,"Login was successful"), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status= status.HTTP_400_BAD_REQUEST)



class DriverRegisterView(generics.GenericAPIView):
    serializer_class = DriverRegistarSerializer
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data= data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

            send_drivers_msg(data['drivers'], request.user.first_name)
            return Response(success_message_helper("",'Driver(s) registered successfully'), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status= status.HTTP_400_BAD_REQUEST)


class AgentVerificationView(generics.CreateAPIView):
    queryset = Agents.objects.all()
    serializer_class = AgentVerification


class UpdateNameView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = UpdateNameSerializer

    def put(self, request):
        serializer = self.serializer_class(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(success_message_helper(serializer.data, "Name successfully updated"), status= status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status= status.HTTP_400_BAD_REQUEST)




# This driver registration view is used when a driver is registering directly without an agent

class SingleDriverRegistrationView(generics.GenericAPIView):
    serializer_class = SingleDriverRegistrationSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self,request):
        data = request.data
        serializer = self.serializer_class(data= data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(success_message_helper(serializer.data, 'Your registration was successful'), status=status.HTTP_200_OK)
        return Response(system_error_message_helper(serializer.errors), status=status.HTTP_400_BAD_REQUEST)




