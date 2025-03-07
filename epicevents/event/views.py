from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from client.models import Client
from usermodel.permissions import RoleBasedPermission
from usermodel.models import CustomUsers
from contract.models import Contract
from .models import Event
from .serializers import EventSerializer


# Create your views here.
class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_object(self):
        try:
            return super().get_object()
        except Event.DoesNotExist:
            return Response({"message": "Event with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        contract_id = self.kwargs['contract_id']
        queryset = Event.objects.filter(contract__id=contract_id)
        return queryset
    
    def create(self, request, *args, **kwargs):
        try:
            client_obj = kwargs.get('client_id')
        except Client.DoesNotExist:
            return Response({"message": "Client with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        try:
            contract_obj = kwargs.get('contract_id')
        except Contract.DoesNotExist:
            return Response({"message": "Contract with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        data = request.data.copy()
        if contract_obj.contract_status == "Signed":
            if request.user.role.role_name == "Management":
                support_contact_id = request.data.get('support_contact')
                if support_contact_id:
                    try:
                        support_contact = CustomUsers.objects.get(id=support_contact_id, role="Support")
                        data['support_contact'] = support_contact.id
                    except CustomUsers.DoesNotExist:
                        return Response({"message": "Invalid Support contact ID."},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"message": "Support contact is required for Management Users."},
                                    status=status.HTTP_400_BAD_REQUEST)
            elif request.user.role.role_name == "Sales":
                if client_obj.sales_contact != request.user:
                    return Response({"message": "You are not assigned to this client."},
                                    status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({"message": "You do not have permission to create event."},
                                status=status.HTTP_403_FORBIDDEN)

            data['contract'] = contract_obj.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            sign_url = f"http://127.0.0.1:8000/api/clients/{client_obj.id}/contracts/{contract_obj.id}/sign/"
            return Response({"message": "Contract is not yet Signed. Please Sign it first",
                             "sign_contract_url": sign_url,
                             "method": "PATCH"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path="assign-support")
    def assign_support_member(self, request, client_id=None, contract_id=None, pk=None):
        try:
            client_obj = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"message": "Client with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        try:
            contract_obj = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            return Response({"message": "Contract with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        event_obj = self.get_object()
        if not event_obj.event_completed:
            partial = True
            serializer = self.get_serializer(event_obj, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            if request.user.role.role_name != "Management":
                return Response({"detail": "You do not have permission to assign support contact"},
                                status=status.HTTP_401_UNAUTHORIZED)
            # set event support member
            support_member = serializer.validated_data.get("support_contact")
            if support_member:
                event_obj.support_contact = support_member
                event_obj.save()
            
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"message": "Event is already completed"},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        client_obj = self.get_object()

        if request.user != client_obj.sales_contact and request.user.role.role_name != 'Management':
            return Response({"message": "You do not have permission to delete this event, as you are not it's owner!"},
                            status=status.HTTP_403_FORBIDDEN)

        super().destroy(request, *args, **kwargs)
        return Response({
                'Message': 'Event has been deleted successfully'
            }, status=status.HTTP_200_OK)        
