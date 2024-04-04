from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .utilities import Google_signin, register_google_user
from .models import CustomUser,PendingUser
import random 


class GoogleSignInSerializer(serializers.Serializer):
    access_token=serializers.CharField(min_length=6)

    def validate_access_token(self, access_token):
        user_data=Google_signin.validate(access_token)
        try:
            user_data['sub']  
        except:
            raise serializers.ValidationError("this token has expired or invalid please try again")
        
        if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
                raise AuthenticationFailed('Could not verify user.')

        email=user_data['email']
        username = email.split('@')[0] 
        provider='google'

        return register_google_user(provider, email, username)

class PhoneOTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    class Meta:
        model = PendingUser
        fields = [
            'phone_number',
            'otp',
            'expiry_time',
        ]

    def validate_phone_number(self, value):
        """
        Validate phone number to ensure it has exactly 10 digits.
        """
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Phone number must be a 10-digit number.")
        return value
        
class OTPVerificationSerializer(serializers.Serializer):
    phone_number=serializers.CharField()
    otp = serializers.CharField(max_length=6)
    

    
         

