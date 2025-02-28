from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .permissions import IsClientOwner
from .models import Client
from .serializers import ClientSerializer


# Create your views here.
class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, IsClientOwner]
    
    def get_queryset(self):
        return Client.objects.all()
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):

        try:
            client_obj = self.get_object()
        except Client.DoesNotExist:
            return Response({"message": "Client with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        if request.user != client_obj.sales_contact and request.user.role.role_name != 'Management':
            return Response({"message": "You do not have permission to update this client, as you are not it's owner!"},
                            status=status.HTTP_403_FORBIDDEN)

        return super().partial_update(request, *args, **kwargs)

