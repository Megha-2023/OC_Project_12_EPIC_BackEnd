""" Module contains class to serialize Clien data"""

from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    """ Client serializer class"""

    class Meta:
        model = Client
        fields = ['id', 'sales_contact', 'first_name', 'last_name',
                  'email', 'mobile', 'company_name', 'client_status']
