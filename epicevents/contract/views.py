""" Module contains ViewSets classes for contract CRUD and search operations"""

import logging
from django.http import Http404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from client.models import Client
from event.models import Event
from event.serializers import EventSerializer
from usermodel.permissions import RoleBasedPermission
from usermodel.models import CustomUsers
from .models import Contract
from .serializers import ContractSerializer

logger = logging.getLogger("contract")


# Create your views here.
class SearchContractViewSet(ModelViewSet):
    """ ViewSet for performing search operations """

    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_queryset(self):
        queryset = Contract.objects.all()

        company_name = self.request.query_params.get('company_name', None)
        client_email = self.request.query_params.get('client_email', None)
        contract_date = self.request.query_params.get('contract_date', None)
        contract_amount = self.request.query_params.get('amount', None)

        if company_name:
            queryset = queryset.filter(client__company_name__icontains=company_name)
        if client_email:
            queryset = queryset.filter(client__email__iexact=client_email)
        if contract_date:
            queryset = queryset.filter(date_created__icontains=contract_date)
        if contract_amount:
            queryset = queryset.filter(amount=contract_amount)
        return queryset


class ContractViewSet(ModelViewSet):
    """ View set for performing Contract CRUD operations"""

    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_object(self):
        try:
            return super().get_object()
        except Http404:
            message = "Contract with given id does not exist"
            logger.error(message)
            return Response({"error": message},
                            status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Contract.objects.filter(client__id=client_id)

    def get_client_obj(self, client_id):
        try:
            client_obj = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            message = "Client with given id does not exist"
            logger.error(message)
            return Response({"error": message},
                            status=status.HTTP_404_NOT_FOUND)
        return client_obj
    
    def create(self, request, *args, **kwargs):
        client_obj = self.get_client_obj(kwargs.get('client_id'))
        
        data = request.data.copy()
        if client_obj.client_status == "Active":
            if request.user.role.role_name == "Management":
                sales_contact_id = request.data.get('sales_contact')
                if sales_contact_id:
                    try:
                        sales_contact = CustomUsers.objects.get(id=sales_contact_id,
                                                                role__role_name="Sales")
                        data['sales_contact'] = sales_contact.id 
                    except CustomUsers.DoesNotExist:
                        message = "Invalid Sales contact ID."
                        logger.error(message)
                        return Response({"error": message},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    message = "Sales contact is required for Management Users."
                    logger.error(message)
                    return Response({"error": message},
                                    status=status.HTTP_400_BAD_REQUEST)
            elif request.user.role.role_name == "Sales":
                if client_obj.sales_contact != request.user:
                    message = "You are not assigned to this client."
                    logger.error(message)
                    return Response({"error": message},
                                    status=status.HTTP_403_FORBIDDEN)
                data['sales_contact'] = request.user.id
            else:
                message = "You do not have permission to create contract."
                logger.error(message)
                return Response({"error": message},
                                status=status.HTTP_403_FORBIDDEN)

            data['client'] = client_obj.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Contract created successfully !")
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
        """ Function for separte endpoint to sign contract"""
        client_obj = self.get_client_obj(client_id)

        # Send custom response if client does not exist
        if isinstance(client_obj, Response):
            return client_obj
        
        contract_obj = self.get_object()

        # Send custom response if contract does not exist
        if isinstance(contract_obj, Response):
            return contract_obj

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

                logger.info("Contract signed successfully !")
                return Response({
                    "message": "Contract updated and signed successfully",
                    "contract": contract_data,
                    "event": event_data
                }, status=status.HTTP_200_OK)
        else:
            message = "Client Status is still 'Lead' Please change it to 'Active'"
            logger.error(message)
            return Response({"error": message},
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        client_obj = self.get_client_obj(kwargs.get('client_id'))
        if isinstance(client_obj, Response):
            return client_obj

        contract_obj = self.get_object()
        if isinstance(contract_obj, Response):
            return contract_obj

        if request.user != contract_obj.sales_contact and request.user.role.role_name != 'Management':
            message = "You do not have permission to delete this contract, you are not its owner!"
            logger.error(message)
            return Response({"error": message},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(contract_obj)
        logger.info("Contract has been deleted successfully")
        return Response({
                "message": "Contract has been deleted successfully"
            }, status=status.HTTP_200_OK)
