from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from client.models import Client
from usermodel.permissions import RoleBasedPermission
from contract.models import Contract
from .models import Event
from .serializers import EventSerializer


# Create your views here.
class EventViewSet(ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_queryset(self):
        contract_id = self.kwargs['contract_id']
        queryset = Event.objects.filter(contract__id=contract_id)
        return queryset
    
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
        
        try:
            event_obj = self.get_object()
        except Event.DoesNotExist:
            return Response({"message": "Event with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
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

        
        
