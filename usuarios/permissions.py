from rest_framework.permissions import BasePermission

from .models import Usuario


class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == Usuario.Rol.ADMINISTRADOR
        )


class IsRequester(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.rol == Usuario.Rol.SOLICITANTE
        )