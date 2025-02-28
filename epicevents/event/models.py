from django.db import models
from usermodel.models import CustomUsers
from contract.models import Contract


# Create your models here.
class Event(models.Model):

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='contract_id')

    # Support member would be only one or multiple???????
    support_contact = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, related_name='event_support_contact', null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    event_completed = models.BooleanField(default=False)
    attendees = models.IntegerField(blank=True, null=True)
    event_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
