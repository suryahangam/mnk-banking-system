# Generated by Django 5.1.1 on 2024-10-07 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_of_birth", models.DateField()),
                ("first_name", models.CharField(max_length=100)),
                (
                    "middle_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("last_name", models.CharField(max_length=100)),
                ("street_address_1", models.CharField(max_length=255)),
                (
                    "street_address_2",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(max_length=100)),
                ("postal_code", models.CharField(max_length=10)),
                ("country", models.CharField(max_length=100)),
                (
                    "account_number",
                    models.CharField(db_index=True, max_length=12, unique=True),
                ),
                (
                    "account_type",
                    models.CharField(
                        choices=[("savings", "Savings"), ("current", "Current")],
                        default="savings",
                        max_length=10,
                    ),
                ),
                (
                    "balance",
                    models.DecimalField(
                        decimal_places=2, default=10000.0, max_digits=15
                    ),
                ),
                (
                    "currency",
                    models.CharField(
                        choices=[("USD", "USD"), ("GBP", "GBP"), ("EUR", "EUR")],
                        default="USD",
                        max_length=3,
                    ),
                ),
                ("date_opened", models.DateField(auto_now_add=True, db_index=True)),
                (
                    "account_status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("suspended", "Suspended"),
                            ("closed", "Closed"),
                        ],
                        db_index=True,
                        default="active",
                        max_length=10,
                    ),
                ),
                (
                    "interest_rate",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
                ),
                (
                    "last_transaction_date",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
            ],
        ),
    ]
