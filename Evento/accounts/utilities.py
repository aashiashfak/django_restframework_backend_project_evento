from google.auth.transport import requests
from google.oauth2 import id_token
from .models import CustomUser
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .manager import CustomUserManager
from datetime import datetime, timedelta


class Google_signin():
    @staticmethod
    def validate(acess_token):
        try:
            id_info=id_token.verify_oauth2_token(acess_token,requests.Request())
            if 'accounts.google.com' in id_info['iss']:
                return id_info
        except Exception as e:
            return None
        
def login_google_user(email, password):
    user=authenticate(email=email,password=password)
    user_tokens=user.tokens()
    return {
       'email':user.email,
       'username':user.username,
       'access_token':str(user_tokens.get('access')),
       'refresh_token':str(user_tokens.get('refresh'))
    }
        
def register_google_user(provider, email,username):
    user=CustomUser.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            login_google_user(email, settings.CUSTOM_PASSWORD_FOR_AUTH)
        else: 
            raise ArithmeticError(
                detail=f'please continue your login with {user[0].auth_provider}'
            )
    else:   
        new_user={
            'email':email,
            'username':username,
            'password':settings.CUSTOM_PASSWORD_FOR_AUTH
        }
        register_user=CustomUser.objects.create_user(**new_user)
        register_user.auth_provider=provider
        register_user.is_active=True
        register_user.save()
        login_google_user(email, settings.CUSTOM_PASSWORD_FOR_AUTH)



#phone number login utilities
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth import authenticate
from .models import CustomUser, PendingUser
# from datetime import datetime, timedelta
import random
from django.core.exceptions import ValidationError
from django.utils import timezone
import requests

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))
def send_otp(phone_number, otp=None):
    sender_id = settings.SPRING_EDGE_SENDER_ID
    api_key = settings.SPRING_EDGE_API_KEY
    
    # Generate a random 6-digit OTP if not provided

    # Define your message
    message = f'Your OTP is: {otp}'
    # Construct the base URL
    base_url = 'https://instantalerts.co/api/web/send/?apikey=' + api_key
    # Construct the complete URL with parameters
    url = base_url + '&sender=' + sender_id + '&to=' + phone_number + '&message=' + message + '&format=json'
    # Send the HTTP GET request to the Spring Edge API
    response = requests.get(url)
    # Check for HTTP codes other than 200
    if response.status_code != 200:
        print('Status:', response, 'Problem with the request.')
        return False

    # Return True if OTP sent successfully
    return True

def login_or_create_user(phone_number, otp):
    try:
        pending_user = PendingUser.objects.get(phone_number=phone_number, otp=otp)
        if pending_user.expiry_time >= timezone.now():
            # OTP is valid and not expired
            user = CustomUser.objects.filter(phone_number=phone_number)
            if user:
                user = authenticate(phone_number=phone_number, password=settings.CUSTOM_PASSWORD_FOR_AUTH)
                if user:
                    return user
            else:
                new_user={
                    'phone_number':phone_number,
                    'password':settings.CUSTOM_PASSWORD_FOR_AUTH
                }
                register_user = CustomUser.objects.create_phone_user(**new_user)
                register_user.set_password(settings.CUSTOM_PASSWORD_FOR_AUTH)
                register_user.is_active = True
                register_user.save()
                return new_user
        else:
            # OTP has expired
            raise ValidationError("OTP has expired")
    except PendingUser.DoesNotExist:
        # Invalid OTP
        raise ValidationError("Invalid OTP")

