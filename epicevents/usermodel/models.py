""" Module contains CustomUser and Roles Schema to store users informations"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.
class Roles(models.Model):
    """ Role model class"""

    role_name = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.role_name


class CustomUsers(AbstractUser):
    """ User model class"""
   
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, related_name='users', blank=True, null=True)

    # to fix conflicts of revers accessor while making migrations
    groups = models.ManyToManyField(Group, related_name='custom_users_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_users_permissions', blank=True)
