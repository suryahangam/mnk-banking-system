from decimal import Decimal
from rest_framework.permissions import BasePermission
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction as db_transaction
from .models import Transaction
from .serializers import (TransactionCreateSerializer,
                          TransactionSerializer, CurrencyConverterSerializer)
from .utils import TransactionFilter, get_latest_exchange_rate
from accounts.models import Account
from accounts.utils import ListPagination
from authentication.permissions import IsTransactionOwnerOrAdmin
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework.views import APIView


class TransactionCreateView(generics.CreateAPIView):
    '''
    This view allows authenticated users to create a new transaction. The transaction data is received
    in the request payload and is validated using the `TransactionCreateSerializer`. If the data is valid,
    a new transaction object is created and saved to the database. The transaction status is set to 'COMPLETED'
    and the serialized data of the transaction is returned in the response.

    Attributes:
        queryset (QuerySet): The queryset of all transactions.
        serializer_class (Serializer): The serializer class used for validating and serializing the transaction data.
        permission_classes (list): The list of permission classes required to access this view.

    Methods:
        create(request, *args, **kwargs): Overrides the default create method to handle the creation of a new transaction.

    Returns:
        A Response object with the following keys:
            - status: The status of the response ('success').
            - message: A success message indicating that the transaction was completed successfully.
            - data: The serialized data of the created transaction.

    Raises:
        - serializers.ValidationError: If the transaction data is invalid.
    '''

    queryset = Transaction.objects.all()
    serializer_class = TransactionCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with db_transaction.atomic():
            transaction = serializer.save()

            # There are no third pary wait times,
            # so we can set the transaction status to 'COMPLETED'
            transaction.status = 'COMPLETED'
            transaction.save()

        return Response({
            'status': 'success',
            'message': 'Transaction completed successfully.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class ListTransactionView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = ListPagination
    filterset_class = TransactionFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    permission_classes = [IsAuthenticated, IsTransactionOwnerOrAdmin]


class DetailTransactionView(generics.RetrieveAPIView):
    """
    A view to retrieve details of a specific transaction.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, IsTransactionOwnerOrAdmin]


class CurrencyConverterView(APIView):
    '''
    API endpoint to display the currency conversion rate before making a transaction.

    This view allows authenticated users to input an amount and a target currency
    for conversion. The API calculates the converted amount based on real-time 
    exchange rates and adds a conversion spread, displaying the total converted amount.
    '''

    permission_classes = [IsAuthenticated]
    serializer_class = CurrencyConverterSerializer

    def post(self, request):
        '''
        Handle POST requests to convert a given amount from the user's account 
        currency to a specified target currency.

        This method first validates the request data using the `CurrencyConverterSerializer`. 
        If the user tries to convert to the same currency, an error response is returned. 
        Otherwise, the conversion is performed using the latest exchange rate and the 
        final amount is adjusted with the conversion spread.

        Args:
            request (Request): The incoming HTTP request containing the conversion data.

        Returns:
            Response: A JSON response containing either the converted amount with 
            exchange rate details or an error message in case of validation failure.
        '''

        account = Account.objects.filter(user=request.user).first()
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from_currency =  account.currency if account else serializer.validated_data['from_currency']

        if serializer.validated_data['to_currency'] == from_currency:
            return Response({
                'status': 'error',
                'message': 'You cannot convert to the same currency.',
                'error': from_currency
            }, status=status.HTTP_400_BAD_REQUEST)

        # to_currency is the target currency for conversion
        to_currency = serializer.validated_data['to_currency']
        amount = serializer.validated_data['amount']

        # get the latest exchange rate and calculate the converted amount
        # add the spread to the total amount
        exchange_rate = get_latest_exchange_rate(from_currency, to_currency)
        converted_amount = Decimal(amount) * Decimal(exchange_rate)
        total_amount = converted_amount + \
            (converted_amount * Decimal(settings.CURRENCY_CONVERSION_SPREAD))

        return Response({
            'status': 'success',
            'message': 'Please note that the displayed converted amounts are based on real-time exchange rates, which may fluctuate. The actual rate at the time of the transaction may differ.',
            'data': {
                'from_currency': from_currency,  # Sender's currency
                'to_currency': to_currency,  # Target currency
                'amount': amount,  # Original amount (In sender's currency)
                # Converted amount (In receiver's currency)
                'converted_amount': converted_amount,
                # Exchange rate from sender's currency to receiver's currency
                'exchange_rate': exchange_rate,
                'spread': settings.CURRENCY_CONVERSION_SPREAD,
            }

        }, status=status.HTTP_200_OK)
