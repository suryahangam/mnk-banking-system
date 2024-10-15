from rest_framework import generics, status, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch

from .models import Account
from .serializers import AccountSerializer
from .utils import ListPagination, AccountFilter
from authentication.permissions import IsAccountOwnerOrAdmin, IsAdmin

from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


class AccountCreateView(generics.CreateAPIView):
    '''
    API view for creating new accounts.

    This view allows authenticated users with admin privileges to create one 
    or multiple accounts. On successful creation, it returns the IDs of the 
    newly created accounts.
    '''

    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        accounts = serializer.save()
        return Response({'status': 'success',
                         'message': 'Account(s) created successfully.',
                         'data': [account.id for account in accounts]},
                        status=status.HTTP_201_CREATED)


class AccountUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAccountOwnerOrAdmin]
    serializer_class = AccountSerializer

    def get_object(self):
        """
        Retrieve the account object. If the user is an admin, return the specified account.
        Otherwise, return the account for the authenticated user.
        """
        user = self.request.user

        # Admins can update any account
        if user.is_admin:
            # Get the account ID from the URL parameters
            account_id = self.kwargs.get('pk')
            return get_object_or_404(Account, id=account_id)

        # Regular users can only update their own account
        return get_object_or_404(Account, user=user)

    def put(self, request, *args, **kwargs):
        # Retrieve the account object
        account = self.get_object()
        serializer = self.get_serializer(
            account, data=request.data, partial=True)  # Allow partial updates

        # Validate the input data
        serializer.is_valid(raise_exception=True)

        # Save the updated account
        serializer.save()

        # Return a success response with updated account data
        return Response({'status': 'success',
                         'message': 'Account updated successfully.',
                         'data': {"account_id": serializer.instance.id}},
                        status=status.HTTP_200_OK)


class AccountListView(generics.ListAPIView):
    """
    A view to list all accounts.
    """
    permission_classes = [IsAuthenticated, IsAccountOwnerOrAdmin]
    queryset = Account.objects.all().prefetch_related(
        Prefetch('sent_transactions'),
        Prefetch('received_transactions')
    )
    serializer_class = AccountSerializer
    pagination_class = ListPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AccountFilter


class AccountDetailView(generics.RetrieveAPIView):
    """
    A view to retrieve details of a specific account.
    """
    permission_classes = [IsAuthenticated, IsAccountOwnerOrAdmin]
    queryset = Account.objects.all().prefetch_related(
        Prefetch('sent_transactions'),
        Prefetch('received_transactions')
    ) 
    serializer_class = AccountSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
