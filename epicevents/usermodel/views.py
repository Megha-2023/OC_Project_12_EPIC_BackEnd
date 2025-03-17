""" Module contains APIView to login Sales and Support Team members """

import logging
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUsers

app_logger = logging.getLogger("epicevents")
logger = logging.getLogger("usermodel")


# Create your views here.
class TeamLoginView(APIView):
    """ Login View"""
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        """ Post method for login endpoint"""

        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            app_logger.error("Username and password are required")
            return Response({
                "error": "Username and password are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # check user exist
        try:
            user_exist = CustomUsers.objects.get(username=username)
        except ObjectDoesNotExist:
            app_logger.error("User does not exist")
            return Response({
                "error": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        # authenticate user
        user = authenticate(username=user_exist.username, password=password)

        if user is None:
            app_logger.error("Invalid Credentials")
            return Response({
                "error": "Invalid Credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)

        refresh_token = RefreshToken.for_user(user)
        logger.info("'%s' logged-in successfully !!", user.get_username())
        return Response({
                    'refresh_token': str(refresh_token),
                    'access': str(refresh_token.access_token)
                    }, status=status.HTTP_200_OK)
