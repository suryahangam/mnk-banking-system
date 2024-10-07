from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    '''
    Custom permission to only allow access to admin users.

    This permission class checks if the requesting user has admin privileges.

    Methods:
        has_permission(request, view): Returns True if the user is an admin, 
        otherwise False.
    '''

    def has_permission(self, request, view):
        return request.user.is_admin


class IsTransactionOwnerOrAdmin(BasePermission):
    '''
    Custom permission to only allow access to the owner of a transaction or an admin.

    This permission class checks if the requesting user is either the sender,
    the receiver of the transaction, or an admin.

    Methods:
        has_object_permission(request, view, obj): 
        Returns True if the user is the owner of the transaction or an admin, otherwise False.
    '''

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin \
            or obj.sender.user == request.user \
            or obj.receiver.user == request.user


class IsAccountOwnerOrAdmin(BasePermission):
    '''
    Custom permission to only allow access to the owner of the account or an admin.

    This permission class checks if the requesting user is the owner of the account
    or an admin.

    Methods:
        has_object_permission(request, view, obj): 
        Returns True if the user is the account owner or an admin, otherwise False.
    '''

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or obj.user == request.user
