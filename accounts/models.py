import random
from django.db import models
from django.contrib.auth import get_user_model


class Account(models.Model):
    ACCOUNT_TYPES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
    ]

    # USD, GBP, EUR
    CURRENCY_CHOICES = [
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
    ]

    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)

    # Address details
    street_address_1 = models.CharField(max_length=255)
    street_address_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    account_number = models.CharField(
        max_length=12, unique=True, db_index=True)
    account_type = models.CharField(
        max_length=10, choices=ACCOUNT_TYPES, default='savings')
    
    # TODO: instead of using default 10000, use currency specific defaults dynamically
    # e.g. 10000 USD, 7500 GBP, 8500 EUR
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=10000.00)
    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default='USD')
    date_opened = models.DateField(auto_now_add=True, db_index=True)
    account_status = models.CharField(max_length=10, choices=ACCOUNT_STATUS_CHOICES,
                                      default='active', db_index=True)
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00)
    last_transaction_date = models.DateTimeField(
        null=True, blank=True, db_index=True)
    
    class Meta:
        unique_together = [
            ('user', 'account_number'), 
            ('user', 'account_type')]

    def __str__(self):
        return f"{self.account_number} ({self.user.email})"

    def update_balance(self, amount, transaction_type):
        """
        Updates the account balance depending on the transaction type.
        'credit' adds to the balance, 'debit' subtracts from the balance.
        """
        if transaction_type == 'credit':
            self.balance += amount
        elif transaction_type == 'debit':
            if self.balance >= amount:
                self.balance -= amount
            else:
                raise ValueError("Insufficient balance")
        self.save()

    def generate_account_number(self):
        """
        Automatically generate a unique account number.
        Example logic: This could be more complex,.
        e.g. bank_id + account_type + unique_id
        bank_id = 099
        account_type = (1, savings) or (2, current)
        unique_id = 8 digits
        """
        bank_id = '099'
        account_type = '1' if self.account_type == 'savings' else '2'

        while True:
            unique_id = random.randint(
                10000000, 99999999)  # 8-digit unique number
            account_number = f"{bank_id}{account_type}{unique_id}"

            # Check for uniqueness in the database
            if not Account.objects.filter(account_number=account_number).exists():
                return account_number  # Return if unique

        # If the loop somehow breaks (shouldn't happen), raise an error or log.
        raise Exception("Unable to generate a unique account number")

    def save(self, *args, **kwargs):
        """
        Override the save method to generate account number before saving if not set.
        """
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)
