import logging
import pyotp
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from django_otp.plugins.otp_totp.models import TOTPDevice
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model

from .serializers import UserRegistrationSerializer
from authentication.notifications.notification_handler import NotificationHandler


logger = logging.getLogger('authentication')


class UserRegistrationView(CreateAPIView):
    '''
    View to handle user registration via a POST request.

    This view allows users to register a new user account. It utilizes the
    UserRegistrationSerializer to validate the input data and create
    a new user instance upon successful validation.

    Attributes:
        serializer_class (UserRegistrationSerializer): The serializer
        used to validate and create user instances.

    Methods:
        post(request, *args, **kwargs): Handles the POST request
        for user registration. Validates the incoming data and
        creates a new user if the data is valid. Returns a response
        with a success message and the newly created user's data.
    '''

    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        '''
        exceptions are handled by the global exception handler and
        field validations + non field validations are handled by the serializer
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {'status': 'success',
                'message': 'User registered successfully.',
                'data': serializer.data
             },
            status=status.HTTP_201_CREATED
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    '''

    Custom view for obtaining a token pair with optional two-factor authentication (2FA).

    This view extends the default TokenObtainPairView to support two-factor authentication
    for users who have enabled it. If 2FA is enabled, an OTP (One-Time Password) is generated
    and sent to the user via their chosen method (email or SMS). The standard token pair response
    is modified to indicate the requirement for 2FA.

    Attributes:
        permission_classes (tuple): Defines permissions for accessing this view, set to AllowAny
                                    to allow public access.

    Methods:
        post(request, *args, **kwargs): Handles POST requests to obtain token pair and manage 2FA.
    '''

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Call the regular JWT authentication first (email & password)
        response = super().post(request, *args, **kwargs)

        user = get_user_model().objects.get(email=request.data['email'])

        # otp_method can be 'email' or 'sms'
        # TODO: Implement validation for otp_method (can only be 'email' or 'sms')
        otp_method = request.data.get('otp_method', 'email')
        mobile_number = request.data.get('mobile_number')

        # 2FA enabled by default
        if user.two_factor_enabled:

            otp_secret = user.otp_secret  # otp_secret is a 16-character base32 secret key

            # Interval in seconds (5 minutes)
            # Interval must match the interval used to verify the OTP
            totp = pyotp.TOTP(otp_secret, interval=300)
            otp_code = totp.now()

            if otp_method == 'sms':
                # If user chooses SMS, ensure they have a mobile number
                # Otherwise, mobile number is optional on registration
                if not user.mobile_number and not mobile_number:
                    return Response({
                                    'status': 'error',
                                    'message': 'Please provide a mobile number for 2FA verification.',
                                    'error': 'Mobile number is required.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif not user.mobile_number:
                    user.mobile_number = mobile_number
                    user.save()

            try:
                # Print on console for development purposes
                print(f'Your 2FA code for Banking System is: {otp_code}')

                # Send the OTP code to the user via their chosen method
                notification = NotificationHandler(
                    user=user,
                    message=f'Your 2FA code for Banking System is: {otp_code}',
                    subject='Your OTP Code',
                    notification_type=otp_method
                )
                notification.send()

            except Exception as e:
                logger.error(f'Error sending 2FA code: {e}')
                # Silently fails for now, can be improved with error handling,
                # but no need to block the user from logging in as user can
                # chhose another OTP method

            # Remove tokens since 2FA is pending
            response.data.pop('refresh', None)
            response.data.pop('access', None)

            # Tell the client that 2FA is required
            return Response({
                'status': 'success',
                'message': f'Please, verify your 2FA code from your {otp_method}.',
                'data': {
                    'user_id': user.id,
                    '2fa_required': True
                }

            }, status=status.HTTP_202_ACCEPTED)

        # If no 2FA is enabled, return the regular tokens
        # two_factor_enabled in CustomUser model is True by default
        return response


class TwoFactorVerifyView(APIView):
    '''
    View for verifying the two-factor authentication (2FA) code provided by the user.

    This view handles the verification of the OTP (One-Time Password) that a user receives
    through their chosen method (email/SMS). Upon successful verification, a new refresh and
    access token is generated for the user, allowing them to access protected resources.

    Methods:
        post(request): Handles POST requests for OTP verification.
    '''

    def post(self, request):
        user_id = request.data.get('user_id')
        otp_code = request.data.get('otp_code')

        if not user_id or not otp_code:
            return Response({'status': 'error',
                             'message': 'Please provide your user ID and OTP code to verify.',
                             'error': 'User ID and OTP code are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.get(id=user_id)

        otp_secret = user.otp_secret

        # Interval in seconds (5 minutes)
        # Interval must match the interval used to generate the OTP
        totp = pyotp.TOTP(otp_secret, interval=300)

        # Verify the OTP entered by the user
        if totp.verify(otp_code):
            refresh = RefreshToken.for_user(user)

            return Response({
                'status': 'success',
                'message': '2FA verification successful.',
                'data': {
                    'user_id': user.id,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'fail',
                'message': 'Invalid OTP code.',
                'error': 'Invalid OTP code.'
            }, status=status.HTTP_400_BAD_REQUEST)


# admin@334#