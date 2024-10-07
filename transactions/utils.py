import json
import django_filters

from django.conf import settings
from .models import Transaction


def get_latest_exchange_rate(from_currency, to_currency):
    '''
    Retrieve the latest exchange rate for converting an amount from one currency to another.

    This function attempts to fetch the current exchange rate using an external API.
    If the API call fails (e.g., due to connectivity issues), it falls back to a local 
    JSON file that contains previously cached exchange rates.

    Args:
        from_currency (str): The currency code to convert from (e.g., 'USD').
        to_currency (str): The currency code to convert to (e.g., 'EUR').

    Returns:
        float: The conversion rate from from_currency to to_currency.

    Raises:
        KeyError: If the conversion rate for the specified currencies is not found
                   in the data retrieved from the API or the local JSON file.

    NOTE: Since the API has free plan limitations, some of the exchange rates may not be available.
    In such cases, the function falls back to the local JSON file for the exchange

    Documentation: https://exchangeratesapi.io/documentation/

    Example:
        API Request: 
            https://api.exchangeratesapi.io/v1/latest
                ? access_key = API_KEY
                & base = USD
                & symbols = GBP,JPY,EUR

        API Response:
            {
                "success": true,
                "timestamp": 1519296206,
                "base": "USD",
                "date": "2021-03-17",
                "rates": {
                    "GBP": 0.72007,
                    "JPY": 107.346001,
                    "EUR": 0.813399,
                }
            }

        Local Json File:
            {
                "USD": {
                    "EUR": 0.85,
                    "GBP": 0.75
                },
                "EUR": {
                    "USD": 1.18,
                    "GBP": 0.88
                },
                "GBP": {
                    "USD": 1.33,
                    "EUR": 1.14
                }
            }

    '''
    try:
        url = f"{settings.EXCHANGE_RATE_API_URL}?access_key={settings.EXCHANGE_RATE_API_KEY}&base={from_currency}&symbols={to_currency}"

        response = requests.get(url)
        data = response.json()
        
        if data['success'] == False:
            raise Exception('Failed to fetch exchange rate from API')
        
        conversion_rate = data['rates'][to_currency]
        return conversion_rate

    except Exception as e:

        with open('exchange_rates.json') as file:
            data = json.load(file)
            conversion_rate = data[from_currency][to_currency]
            return conversion_rate


class TransactionFilter(django_filters.FilterSet):
    '''
    This class provides a filter set for the Transaction model.
    '''
    sender = django_filters.NumberFilter(
        field_name='sender__user', lookup_expr='exact')
    receiver = django_filters.NumberFilter(
        field_name='receiver__user', lookup_expr='exact')
    amount_min = django_filters.NumberFilter(
        field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(
        field_name='amount', lookup_expr='lte')
    status = django_filters.ChoiceFilter(
        field_name='status', choices=Transaction.STATUS_CHOICES)
    timestamp = django_filters.DateTimeFilter(
        field_name='timestamp', lookup_expr='exact')

    class Meta:
        model = Transaction
        fields = [
            'sender',
            'receiver',
            'amount_min',
            'amount_max',
            'status',
            'timestamp',
        ]
