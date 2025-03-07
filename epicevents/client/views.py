""" Module contains ClientViewSet class for client CRUD operations"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from usermodel.permissions import RoleBasedPermission
from usermodel.models import CustomUsers
from .models import Client
from .serializers import ClientSerializer


# Create your views here.
class ClientViewSet(ModelViewSet):
    """ View set for performing Client CRUD operations"""

    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_object(self):
        try:
            return super().get_object()
        except Client.DoesNotExist:
            return Response({"message": "Client with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        queryset = Client.objects.all()
        company_name = self.request.query_params.get('name', None)
        client_email = self.request.query_params.get('email', None)

        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)
        if client_email:
            queryset = queryset.filter(email__iexact=client_email)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if request.user.role.role_name == "Management":
            sales_contact_id = request.data.get('sales_contact')
            if sales_contact_id:
                try:
                    sales_contact = CustomUsers.objects.get(id=sales_contact_id, role="Sales")
                    data['sales_contact'] = sales_contact.id
                except CustomUsers.DoesNotExist:
                    return Response({"message": "Invalid Sales contact ID."},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "Sales contact is required for Management Users."},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.user.role.role_name == "Sales":
            data['sales_contact'] = request.user.id
        else:
            return Response({"message": "You do not have permission to create contract."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='activate-client')
    def activate_client(self, request, pk=None):
        client_obj = self.get_object()

        if request.user != client_obj.sales_contact and request.user.role.role_name != 'Management':
            return Response(
                {"message": "You do not have permission to update this client, you are not its owner!"},
                status=status.HTTP_403_FORBIDDEN)

        partial = True
        serializer = self.get_serializer(client_obj, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data.get("client_status") == "Active" and client_obj.client_status != "Active":
            client_obj.client_status = "Active"
            client_obj.save()

        return Response({
            "message": "Client status updated successfully",
            "client": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        client_obj = self.get_object()

        if request.user != client_obj.sales_contact and request.user.role.role_name != 'Management':
            return Response(
                {"message": "You do not have permission to delete this client, you are not its owner!"},
                status=status.HTTP_403_FORBIDDEN)

        super().destroy(request, *args, **kwargs)
        return Response({
                'Message': 'Client has been deleted successfully'
            }, status=status.HTTP_200_OK)

