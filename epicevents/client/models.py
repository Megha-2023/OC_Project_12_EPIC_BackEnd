""" Module contains Client Schema"""

from django.db import models
from usermodel.models import CustomUsers


# Create your models here.
class Client(models.Model):
    """ Client model class"""

    CLIENT_STATUS_CHOICES = [
        ('Lead', 'Lead'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    ]

    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=60)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    client_status = models.CharField(max_length=15, choices=CLIENT_STATUS_CHOICES, default='Lead')

    # Sales member would be only one-one with client
    sales_contact = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, related_name='client_sales_contact')
