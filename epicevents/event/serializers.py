""" Module contains class to serialize Evnet data"""

from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """ Event serializer class """
    class Meta:
        model = Event
        fields = "__all__"
