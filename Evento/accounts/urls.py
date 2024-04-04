from .views import GoogleOauthSignInview,PhoneOTPRequestView,OTPVerificationView
from django.urls import path


urlpatterns = [
    path('google/oauth/', GoogleOauthSignInview.as_view(), name='google_oauth_signin'),
    path('phone-otp-request/', PhoneOTPRequestView.as_view(), name='phone_otp_request'),
    path('otp-verification/', OTPVerificationView.as_view(), name='otp_verification'),


]