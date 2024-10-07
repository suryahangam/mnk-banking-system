
import decimal
from django.conf import settings
from rest_framework import serializers

from .models import Transaction
from .utils import get_latest_exchange_rate
from accounts.models import Account


class TransactionSerializer(serializers.ModelSerializer):
    '''
    Serializer class for the Transaction listing and detail views.

    This serializer is used to convert Transaction model instances into JSON
    representation and vice versa. It defines the fields that should be included
    in the serialized output and provides methods for custom field serialization.

    Fields:
    - id: The unique identifier of the transaction.
    - sender_email: The email address of the sender associated with the transaction.
    - receiver_email: The email address of the receiver associated with the transaction.
    - amount: The amount of the transaction.
    - timestamp: The timestamp when the transaction occurred.
    - status: The status of the transaction.
    - description: The description of the transaction.
    - transaction_type: The type of the transaction.

    Methods:
    - get_transaction_type: Returns the transaction type based on the user making the request.

    Usage:
    1. Create an instance of TransactionSerializer with the transaction data.
    2. Call the serializer's `is_valid()` method to validate the input data.
    3. Access the serialized data using the `data` attribute.
    '''

    sender_email = serializers.EmailField(
        source='sender.user.email', read_only=True)
    receiver_email = serializers.EmailField(
        source='receiver.user.email', read_only=True)
    transaction_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'sender_email', 'receiver_email', 'amount',
                  'timestamp', 'status', 'description', 'transaction_type']

    def get_transaction_type(self, obj):
        '''
        Returns the transaction type based on the user making the request.

        Parameters:
        - obj: The Transaction model instance.

        Returns:
        - The transaction type as a string.
        '''

        user = self.context['request'].user
        return obj.get_transaction_type(user)


class TransactionCreateSerializer(serializers.ModelSerializer):
    '''
    Serializer for creating a transaction between two accounts. This handles
    validating the sender's balance, ensuring the sender and receiver are different,
    and processing currency conversion if necessary.

    Fields:
        - receiver_account_number: The account number of the receiver (write-only).
        - amount: The amount to be transferred.
        - description: A description of the transaction.
        - to_currency: The currency in which the receiver expects to receive the funds.
        - & transaction fields (id, sender, receiver, currency, exchange_rate, timestamp, status).

    Methods:
        - validate_to_currency: Ensures the selected currency is one of the supported currencies.
        - validate_amount: Ensures the transaction amount is greater than zero.
        - validate: General validation ensuring sufficient balance, different sender and receiver, and currency match.
        - get_sender_account: Retrieves the sender's account based on the current authenticated user.
        - get_receiver_account: Retrieves the receiver's account based on the provided account number.
        - create: Handles the transaction creation, including currency conversion if needed.
        - convert_currency: Converts the amount based on exchange rates and adds a spread.
        - update_account: Updates the balances of both sender and receiver's accounts.

    Note: Important variables to take note of
        - sender_account: The account of the authenticated user initiating the transaction.
        - receiver_account: The account of the receiver based on the provided account number.
        - total_amount: The final amount to be transferred after currency conversion.
        - exchange_rate: The exchange rate used for currency conversion.
        - spread: The spread added to the converted amount to account for fluctuations.
    '''

    receiver_account_number = serializers.CharField(write_only=True)
    to_currency = serializers.ChoiceField(choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
    ])

    class Meta:
        model = Transaction
        fields = ['receiver_account_number',
                  'amount', 'description', 'to_currency']

    def validate_to_currency(self, value):
        choices = [choice for choice in self.fields['to_currency'].choices]
        if value not in choices:
            raise serializers.ValidationError(
                f"Our system does not support exchange to {value} currency.")
        return value

    def validate_amount(self, value):
        # Additional validation for amount can be added here
        if value <= 0:
            raise serializers.ValidationError(
                "The amount must be greater than zero.")
        return value

    def validate(self, attrs):
        # Get the authenticated user's account
        sender_account = self.get_sender_account()

        # Get receiver's account using the receiver_account_number from validated data
        receiver_account_number = attrs.get('receiver_account_number')
        receiver_account = self.get_receiver_account(receiver_account_number)

        # Validate that the sender and receiver are not the same
        if sender_account == receiver_account:
            raise serializers.ValidationError(
                "Sender and receiver cannot be the same.")

        # Check if sender has enough balance
        if sender_account.balance < attrs['amount']:
            raise serializers.ValidationError(
                "Insufficient balance in the sender's account.")

        # Check if currency matches receiver's account currency
        if attrs['to_currency'] != receiver_account.currency:
            raise serializers.ValidationError(
                "Currency must match receiver's account currency.")

        # Store the accounts for later use in create method
        attrs['sender_account'] = sender_account
        attrs['receiver_account'] = receiver_account
        return attrs

    def get_sender_account(self):
        user = self.context['request'].user
        sender_account = Account.objects.filter(
            user=user, account_status='active').first()

        if sender_account is None:
            raise serializers.ValidationError(
                "Sender does not have an active account.")

        return sender_account

    def get_receiver_account(self, account_number):
        try:
            return Account.objects.filter(account_number=account_number,
                                          account_status='active').first()
        except Account.DoesNotExist:
            raise serializers.ValidationError(
                f"Account with number {account_number} does not exist.")

    def create(self, validated_data):
        sender_account = validated_data.pop('sender_account')
        receiver_account = validated_data.pop('receiver_account')

        validated_data['currency'] = sender_account.currency
        _ = validated_data.pop('receiver_account_number')

        # Set the total amount to the original amount
        total_amount = validated_data['amount']

        # Check if conversion is required
        if sender_account.currency != receiver_account.currency:

            # Since the sender and receiver have different currencies,
            # convert the amount to the receiver's currency
            # and update the total amount and exchange rate
            total_amount, exchange_rate = self.convert_currency(
                validated_data['amount'],
                sender_account.currency,
                receiver_account.currency
            )

            # If the currency conversion is not required, the exchange rate is empty
            validated_data['exchange_rate'] = exchange_rate

        # Create the transaction with the found accounts
        transaction = Transaction.objects.create(
            sender=sender_account,
            receiver=receiver_account,
            **validated_data
        )

        # (Important) Update the account balances.
        # Because of currency conversion, sender's and
        # receiver's amounts are tracked differently
        self.update_account(
            sender_account=sender_account,
            receiver_account=receiver_account,
            sender_amount=validated_data['amount'],
            receiver_amount=total_amount
        )
        return transaction

    def convert_currency(self, amount, from_currency, to_currency):
        # Convert the amount from one currency to another and add a spread
        conversion_rate = get_latest_exchange_rate(from_currency, to_currency)
        spread = decimal.Decimal(settings.CURRENCY_CONVERSION_SPREAD)

        converted_amount = decimal.Decimal(
            amount) * decimal.Decimal(conversion_rate)
        spread_amount = converted_amount * spread

        total_amount = converted_amount + spread_amount
        return total_amount, conversion_rate

    def update_account(self, sender_account, receiver_account, sender_amount, receiver_amount):

        # update_balance is a method in the Account model
        # update_balance(amount: Decimal, transaction_type: str)
        sender_account.update_balance(sender_amount, 'debit')
        receiver_account.update_balance(receiver_amount, 'credit')


class CurrencyConverterSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    to_currency = serializers.ChoiceField(choices=[
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('GBP', 'GBP'),
    ])

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "The amount must be greater than zero.")
        return value

    def validate_to_currency(self, value):
        choices = [choice for choice in self.fields['to_currency'].choices]
        if value not in choices:
            raise serializers.ValidationError(
                f"Our system does not support {value} currency.")
        return value
