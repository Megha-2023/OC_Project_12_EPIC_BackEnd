""" Module contains class to serialize Contract data"""

from rest_framework import serializers
from .models import Contract


class ContractSerializer(serializers.ModelSerializer):
    """ Contract serializer class"""
    class Meta:
        model = Contract
        fields = "__all__"
