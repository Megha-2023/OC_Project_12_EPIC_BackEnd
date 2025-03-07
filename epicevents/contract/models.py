""" Module contains Contract Schema"""

from django.db import models
from usermodel.models import CustomUsers
from client.models import Client


# Create your models here.
class Contract(models.Model):
    """ Contract model class"""

    CONTRACT_STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Signed', 'Signed')
    ]

    # Support member would be only one-one with contract
    sales_contact = models.ForeignKey(CustomUsers, on_delete=models.CASCADE,
                                      related_name='contract_sales_contact')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='client_id')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    contract_status = models.CharField(max_length=15, choices=CONTRACT_STATUS_CHOICES,
                                       default='Open')
    amount = models.FloatField()
    payment_due = models.DateTimeField()
