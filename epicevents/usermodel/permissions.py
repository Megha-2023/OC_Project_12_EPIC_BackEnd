""" Module contains custom permissions class"""

from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):
    """
        - Management team has full access
        - Everyon has read-only access to all models.
        - Sales team can edit clients and realted contracts/events
        - Support team can edit events they own.
    """

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        if request.user.is_staff:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True

        if request.user.is_staff:
            return True

        # Sales team can edit clients and related contracts/events
        if request.user.role.role_name == "Sales":
            if hasattr(obj, "sales_contact") and obj.sales_contact == request.user:
                return True

            if hasattr(obj, "client") and obj.client.sales_contact == request.user:
                return True

        # Support team can only edit events they own.
        if request.user.role.role_name == "Support":
            if hasattr(obj, "support_contact") and obj.support_contact == request.user:
                return True

        return False
