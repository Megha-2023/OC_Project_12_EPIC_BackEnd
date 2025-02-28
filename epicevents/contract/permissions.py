from rest_framework.permissions import BasePermission


class IsContractOwner(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if hasattr(request.user, 'role') and request.user.role is not None:
            return request.user.role.role_name in ['Sales', 'Management']

        return False

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True

        return obj.sales_contact == request.user or request.user.role.role_name == 'Management'
