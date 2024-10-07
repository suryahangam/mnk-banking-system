import re
import datetime

from rest_framework import serializers
from authentication.serializers import UserListSerializer
from transactions.serializers import TransactionSerializer
from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    '''
    Serializer for the Account model.

    This serializer handles the serialization and validation of Account
    instances. It includes fields related to user information and account 
    details, and also handles transactions related to the account.

    Attributes:
        user_details (UserListSerializer): Serializer for the associated user details.
        transactions (SerializerMethodField): Custom field to retrieve the account's transactions.
        &
        Account model fields: (id, user, first_name, middle_name, last_name, date_of_birth, 
        street_address_1, street_address_2, city, state, postal_code, country, account_type, 
        interest_rate, balance, currency, date_opened, account_number)

    Methods:
        get_transactions(obj): Retrieves a list of transactions associated with the account.
        validate_date_of_birth(value): Validates that the date of birth is in the past.
        validate_postal_code(value): Validates that the postal code follows the UK format.
        validate_currency(value): Ensures the currency is one of the accepted options.
        validate_interest_rate(value): Ensures that the interest rate is not negative.
        create(validated_data): Creates a new Account instance or bulk creates if provided a list.
        update(instance, validated_data): Updates the existing Account instance with validated data.
    '''

    user_details = UserListSerializer(
        source='user', read_only=True)  # To display user details
    transactions = serializers.SerializerMethodField(
        read_only=True)  # To display all related transactions

    class Meta:
        model = Account
        fields = [
            'id',
            'user',
            'first_name',
            'middle_name',
            'last_name',
            'user_details',
            'date_of_birth',
            'street_address_1',
            'street_address_2',
            'city',
            'state',
            'postal_code',
            'country',
            'account_type',
            'interest_rate',
            'balance',
            'currency',
            'date_opened',
            'account_number',
            'transactions',
        ]
        read_only_fields = [
            'id',
            'balance',
            'currency',
            'date_opened',
            'account_number',
            'transactions',
        ]

    def get_transactions(self, obj):
        '''
        Retrieve the list of transactions associated with the account.

        Combines both sent and received transactions for the specified account.

        Args:
            obj (Account): The account instance for which transactions are retrieved.

        Returns:
            list: Serialized list of transactions related to the account.
        '''

        sent_transactions = obj.sent_transactions.all()
        received_transactions = obj.received_transactions.all()
        all_transactions = sent_transactions | received_transactions
        request = self.context.get('request')
        return TransactionSerializer(all_transactions, many=True, context={'request': request}).data

    def validate_date_of_birth(self, value):
        '''
        Check that the date of birth is in the past.
        '''
        if value >= datetime.date.today():
            raise serializers.ValidationError(
                "Date of birth must be in the past.")
        return value

    def validate_postal_code(self, value):
        '''
        Check that the postal code follows the UK format.
        '''
        # Regular expression pattern for UK postal codes
        postcode_regex = r'^([Gg][Ii][Rr] 0[Aa]{2}|[A-Za-z]{1,2}[0-9][0-9]?[A-Za-z]? ?[0-9][A-Za-z]{2}|[A-Za-z]{1,2}[0-9][A-Za-z]? ?[0-9][A-Za-z]{2})$'
        if not re.match(postcode_regex, value):
            raise serializers.ValidationError("Invalid postal code format.")
        return value

    def validate_currency(self, value):
        '''
        Ensure the currency is one of the accepted options.
        Accepted currencies: USD, GBP, EUR.
        '''
        valid_currencies = [choice[0] for choice in Account.CURRENCY_CHOICES]
        if value not in valid_currencies:
            raise serializers.ValidationError(
                "Invalid currency. Must be one of: USD, GBP, EUR.")
        return value

    def validate_interest_rate(self, value):
        '''
        Ensure that the interest rate is not negative.
        '''
        if value < 0:
            raise serializers.ValidationError(
                "Interest rate cannot be negative.")
        return value

    def create(self, validated_data):
        '''
        Create a new Account instance or bulk create if provided a list.
        In this way we can create multiple accounts at once and single account as well.
        '''
        if isinstance(validated_data, list):
            return Account.objects.bulk_create(
                [Account(**account_data) for account_data in validated_data]
            )
        return Account.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Update instance attributes with validated data
        for attr, value in validated_data.items():
            if attr in [
                'first_name',
                'middle_name',
                'last_name',
                'user',
                'date_of_birth',
                'street_address_1',
                'street_address_2',
                'city',
                'state',
                'postal_code',
                'country',
                'account_type',
                'interest_rate'
            ]:
                setattr(instance, attr, value)

        instance.save()
        return instance
