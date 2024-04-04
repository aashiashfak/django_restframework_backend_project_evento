from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from .serializers import GoogleSignInSerializer,PhoneOTPRequestSerializer, OTPVerificationSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import PendingUser
from datetime import datetime, timedelta
from django.conf import settings


from .utilities import send_otp, login_or_create_user, generate_otp

# Create your views here.

class GoogleOauthSignInview(GenericAPIView):
    serializer_class=GoogleSignInSerializer

    def post(self, request):
        print(request.data)
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=((serializer.validated_data)['access_token'])
        return Response(data, status=status.HTTP_200_OK) 
    



class PhoneOTPRequestView(APIView):
    def post(self, request):
        serializer = PhoneOTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            otp = generate_otp()
            expiry_time = datetime.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
            pending_user = PendingUser.objects.create(phone_number=phone_number, otp=otp, expiry_time=expiry_time)
            try:
                send_otp(phone_number, otp)  # Send OTP to the provided phone number
                return Response({"detail": "OTP sent successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                # If sending OTP fails, delete the pending user
                pending_user.delete()
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.utils import timezone

class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            otp = serializer.validated_data['otp']
            phone_number = serializer.validated_data['phone_number']
            try:
                pending_user = PendingUser.objects.get(phone_number=phone_number, otp=otp)
                if pending_user.expiry_time >= timezone.now():  # Use timezone.now() instead of datetime.now()
                    # OTP is valid and not expired, login or create user
                    user = login_or_create_user(phone_number, otp)
                    # Delete the pending user after successful verification
                    pending_user.delete()
                    return Response({"detail": "User logged in successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)
            except PendingUser.DoesNotExist:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
