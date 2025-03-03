from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from client.models import Client
from event.models import Event
from event.serializers import EventSerializer
from usermodel.permissions import RoleBasedPermission
from .models import Contract
from .serializers import ContractSerializer

# Create your views here.
class ContractViewSet(ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    
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
        data['client'] = client_obj.id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    @action(detail=True, methods=['patch'], url_path='sign')
    def sign_contract(self, request, client_id=None, pk=None):
        try:
            client_obj = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response({"message": "Client with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        try:
            contract_obj = self.get_object()
        except Contract.DoesNotExist:
            return Response({"message": "Contract with given id does not exist"},
                            status=status.HTTP_404_NOT_FOUND)
        
        partial = True

        serializer = self.get_serializer(contract_obj, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # if contract status is changed to 'Signed' an event object corresponding to contract is created
        if serializer.validated_data.get("contract_status") == "Signed" and contract_obj.contract_status != "Signed":
            # set contract status 'Signed'
            contract_obj.contract_status = "Signed"
            contract_obj.save()

            # check client status if it is 'Active'
            if client_obj.client_status != "Active":
                client_obj.client_status = "Active"
                client_obj.save()

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
