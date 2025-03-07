from rest_framework.viewsets import ModelViewSet
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from client.models import Client
from client.views import ClientViewSet
from event.models import Event
from event.serializers import EventSerializer
from usermodel.permissions import RoleBasedPermission
from usermodel.models import CustomUsers
from .models import Contract
from .serializers import ContractSerializer

# Create your views here.
class ContractViewSet(ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    
    def get_object(self):
        try:
            return super().get_object()
        except Contract.DoesNotExist:
            return Response({"message": "Contract with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
    
    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Contract.objects.filter(client__id=client_id)
    
    def create(self, request, *args, **kwargs):
        client_id = kwargs.get('client_id')
        try:
            client_obj = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"message": "Client with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        if client_obj.client_status == "Active":
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
                if client_obj.sales_contact != request.user:
                    return Response({"message": "You are not assigned to this client."},
                                    status=status.HTTP_403_FORBIDDEN)
                data['sales_contact'] = request.user.id

            else:
                return Response({"message": "You do not have permission to create contract."},
                                status=status.HTTP_403_FORBIDDEN)

            data['client'] = client_obj.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            activate_url = f"http://127.0.0.1:8000/api/clients/{client_id}/activate-client/"
            return Response({"message": "Client Status is still 'Lead'. Please change it to 'Active'",
                             "activate_client_url": activate_url,
                             "method": "PATCH"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='sign')
    def sign_contract(self, request, client_id=None, pk=None):
        try:
            client_obj = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"message": "Client with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

        contract_obj = self.get_object()
        
        partial = True

        serializer = self.get_serializer(contract_obj, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # check client status if it is 'Active'
        if client_obj.client_status == "Active":
            # if contract status is changed to 'Signed' an event object corresponding to contract is created
            if serializer.validated_data.get("contract_status") == "Signed" and contract_obj.contract_status != "Signed":
                # set contract status 'Signed'
                contract_obj.contract_status = "Signed"
                contract_obj.save()

                # create an event object
                event_obj = Event.objects.create(
                    contract=contract_obj
                )
                event_data = EventSerializer(event_obj).data
                contract_data = serializer.data

                return Response({
                    "message": "Contract updated and signed successfully",
                    "contract": contract_data,
                    "event": event_data
                }, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Client Status is still 'Lead'. Please change it to 'Active'"},
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        client_obj = self.get_object()

        if request.user != client_obj.sales_contact and request.user.role.role_name != 'Management':
            return Response({"message": "You do not have permission to delete this contract, as you are not it's owner!"},
                            status=status.HTTP_403_FORBIDDEN)

        super().destroy(request, *args, **kwargs)
        return Response({
                'Message': 'Contract has been deleted successfully'
            }, status=status.HTTP_200_OK)
