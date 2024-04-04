from rest_framework import generics, status
from rest_framework.response import Response
from .models import Vendor
from .serializers import VendorSerializer
from .utilities import send_otp_email
from rest_framework.views import APIView
import random

class VendorSignUpView(APIView):
    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Store the vendor details in the session
                request.session['vendor_signup_data'] = serializer.validated_data

                # Generate OTP (you can implement your own logic here)
                otp = ''.join(random.choices('0123456789', k=6))
                request.session['vendor_signup_otp'] = otp

                # Send OTP to the provided email
                send_otp_email(serializer.validated_data['email'], serializer.validated_data['contact_name'], otp)

                # Return success response with a message
                return Response({"detail": "An OTP has been sent to your email address. Please use it to complete the sign-up process."}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": "Failed to send OTP email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from .serializers import VendorSerializer, VerifyOTPSerializer


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            entered_otp = serializer.validated_data['otp']
            session_otp = request.session.get('vendor_signup_otp')

            if not session_otp:
                return Response({"error": "OTP not found in session"}, status=status.HTTP_400_BAD_REQUEST)

            if entered_otp == session_otp:
                # OTP matches, create the vendor user
                vendor_serializer = VendorSerializer(data=request.session.get('vendor_signup_data'))
                if vendor_serializer.is_valid():
                    vendor = vendor_serializer.save(is_active=True, is_vendor=True)
                    return Response({"detail": "Vendor user created successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response(vendor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def create_vendor_user(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            try:
                vendor = serializer.save(is_active=True, is_vendor=True)
                return Response({"detail": "Vendor user created successfully"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": "Failed to create vendor user"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Return validation errors if serializer is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
