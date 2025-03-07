from rest_framework import permissions


class IsResidentAndHasApartment(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.status == "Resident" and
            request.user.residents.exists()
        )

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.status == "Admin"


class IsSecurityUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.status == "Security"


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
