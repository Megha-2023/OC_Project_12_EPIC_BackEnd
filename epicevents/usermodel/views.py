from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.views import APIView
from .models import CustomUsers


# Create your views here.
class TeamLoginView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                "detail": "Username and password are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # check user exist
        try:
            user_exist = CustomUsers.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({
                "detail": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # authenticate user
        user = authenticate(username=user_exist.username, password=password)

        if user is None:
            return Response({
                "detail": "Invalid Credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)
  
        refresh_token = RefreshToken.for_user(user)
        return Response({
                    'refresh_token': str(refresh_token),
                    'access': str(refresh_token.access_token)
                    }, status=status.HTTP_200_OK)

