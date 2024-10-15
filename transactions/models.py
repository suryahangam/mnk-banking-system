from django.db import models
from django.conf import settings
from accounts.models import Account


class Transaction(models.Model):
    STATUS_CHOICES = [("PENDING", "PENDING"), ("COMPLETED",
                      "COMPLETED"), ("FAILED", "FAILED")]

    sender = models.ForeignKey(
        Account,
        related_name='sent_transactions',
        on_delete=models.PROTECT,
        db_index=True
    )
    receiver = models.ForeignKey(
        Account,
        related_name='received_transactions',
        on_delete=models.PROTECT,
        db_index=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, db_index=True) # amount will be in sender's currency
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    # e.g., PENDING, COMPLETED, FAILED
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING", db_index=True)
    description = models.TextField(null=True, blank=True)
    exchange_rate = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, ) # Sender's currency
    to_currency = models.CharField(max_length=3, null=True) # Receiver's currency

    def __str__(self):
        return f"{self.sender.user.email} -> {self.receiver.user.email}({self.amount}"

    class Meta:
        ordering = ['-timestamp']

    def get_transaction_type(self, user):
        if user == self.sender.user:
            return "DEBIT"
        elif user == self.receiver.user:
            return "CREDIT"
        return "UNKNOWN"
