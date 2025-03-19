""" Module contains ViewSets classes for event CRUD and search operations"""

import logging
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

logger = logging.getLogger("event")


# Create your views here.
class SerachEventViewSet(ModelViewSet):
    """ ViewSet for performing search operations """

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_queryset(self):
        queryset = Event.objects.all()

        company_name = self.request.query_params.get('company_name', None)
        client_email = self.request.query_params.get('client_email', None)
        event_date = self.request.query_params.get('event_date', None)

        if company_name:
            queryset = queryset.filter(contract__client__company_name__icontains=company_name)
        if client_email:
            queryset = queryset.filter(contract__client__email__iexact=client_email)
        if event_date:
            queryset = queryset.filter(event_date__icontains=event_date)
        return queryset


class EventViewSet(ModelViewSet):
    """ View set for performing Event CRUD operations"""
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]

    def get_object(self):
        try:
            return super().get_object()
        except Event.DoesNotExist:
            message = "Event with given id does not exist"
            logger.error(message)
            return Response({"error": message},
                            status=status.HTTP_404_NOT_FOUND)

    def get_queryset(self):
        contract_id = self.kwargs['contract_id']
        queryset = Event.objects.filter(contract__id=contract_id)
        return queryset

    def get_client_obj(self, client_id):
        try:
            client_obj = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            message = "Client with given id does not exist"
            logger.error(message)
            return Response({"error": message},
                            status=status.HTTP_404_NOT_FOUND)
        return client_obj
    
    def get_contract_obj(self, contract_id):
        try:
            contract_obj = Contract.objects.get(id=contract_id)
        except Contract.DoesNotExist:
            message = "Contract with given id does not exist"
            logger.error(message)
            return Response({"error": message},
                            status=status.HTTP_404_NOT_FOUND)
        return contract_obj
    

    def create(self, request, *args, **kwargs):
        client_obj = self.get_client_obj(kwargs.get('client_id'))

        if isinstance(client_obj, Response):
            return client_obj

        contract_obj = self.get_contract_obj(kwargs.get('contract_id'))

        if isinstance(contract_obj, Response):
            return contract_obj

        data = request.data.copy()
        if contract_obj.contract_status == "Signed":
            if request.user.role.role_name == "Management":
                support_contact_id = request.data.get('support_contact')
                if support_contact_id:
                    try:
                        support_contact = CustomUsers.objects.get(id=support_contact_id,
                                                                  role__role_name="Support")
                        data['support_contact'] = support_contact.id
                    except CustomUsers.DoesNotExist:
                        message = "Invalid Support contact ID."
                        logger.error(message)
                        return Response({"error": message},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    message = "Support contact is required for Management Users."
                    logger.error(message)
                    return Response({"error": message},
                                    status=status.HTTP_400_BAD_REQUEST)
            elif request.user.role.role_name == "Sales":
                if client_obj.sales_contact != request.user:
                    message = "You are not assigned to this client."
                    logger.error(message)
                    return Response({"error": message},
                                    status=status.HTTP_403_FORBIDDEN)
            else:
                message = "You do not have permission to create event."
                logger.error(message)
                return Response({"error": message},
                                status=status.HTTP_403_FORBIDDEN)

            data['contract'] = contract_obj.id
            serializer = self.get_serializer(data=data)
            if serializer.is_valid():
                serializer.save()
                logger.info("Event created successfully !")
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
        """ Function assign support member to an event by management team"""
        client_obj = self.get_client_obj(client_id)

        if isinstance(client_obj, Response):
            return client_obj

        contract_obj = self.get_contract_obj(contract_id)

        if isinstance(contract_obj, Response):
            return contract_obj

        event_obj = self.get_object()
        if not event_obj.event_completed:
            partial = True
            serializer = self.get_serializer(event_obj, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            if request.user.role.role_name != "Management":
                return Response({"detail": "You do not have permission to assign support contact"},
                                status=status.HTTP_401_UNAUTHORIZED)

            # set event support contact
            support_contact_id = request.data.get("support_contact")
            try:
                support_contact = CustomUsers.objects.get(id=support_contact_id, role__role_name="Support")
                event_obj.support_contact = support_contact
                event_obj.save()
                
            except CustomUsers.DoesNotExist:
                message = "Invalid Support contact ID."
                logger.error(message)
                return Response({"error": message},
                                status=status.HTTP_400_BAD_REQUEST)

            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"message": "Event is already completed"},
                        status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        client_obj = self.get_client_obj(kwargs.get('client_id'))
        if isinstance(client_obj, Response):
            return client_obj

        contract_obj = self.get_contract_obj(kwargs.get('contract_id'))
        if isinstance(contract_obj, Response):
            return contract_obj
        
        event_obj = self.get_object()
        if isinstance(event_obj, Response):
            return event_obj

        if request.user != event_obj.support_contact and request.user.role.role_name != 'Management':
            return Response({"message": "You do not have permission to delete this event, you are not its owner!"},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(event_obj)
        return Response({
                'Message': 'Event has been deleted successfully'
            }, status=status.HTTP_200_OK)
    
