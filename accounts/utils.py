from rest_framework.pagination import PageNumberPagination
import django_filters
from .models import Account


class ListPagination(PageNumberPagination):
    '''
    ustom pagination class for listing API responses.

    This pagination class inherits from Django REST framework's 
    PageNumberPagination and provides a way to paginate querysets.

    Attributes:
        page_size (int): The default number of items per page.
        page_size_query_param (str): The query parameter used to customize page size.
        max_page_size (int): The maximum number of items allowed per page.

    Usage:
        To use this pagination, set it in your API views or in the settings.
    '''

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AccountFilter(django_filters.FilterSet):
    '''
    Filter class for querying Account model instances.

    This filter class defines various filters that can be applied 
    to the Account model fields to enable complex querying.

    Attributes:
        account_type (CharFilter): Filter for exact match on account type.
        user (NumberFilter): Filter for exact match on user ID.
        date_opened (DateFilter): Filter for exact match on the date the account was opened.
        balance_min (NumberFilter): Filter for accounts with balance greater than or equal to a specified value.
        balance_max (NumberFilter): Filter for accounts with balance less than or equal to a specified value.

    Meta:
        model (Account): The model that this filter set is applied to.
        fields (list): The fields available for filtering in the API requests.

    TODO: Make single filter for all models that supports dynamic fields and lookups.
    '''

    account_type = django_filters.CharFilter(
        field_name='account_type', lookup_expr='iexact')
    user = django_filters.NumberFilter(field_name='user', lookup_expr='iexact')
    date_opened = django_filters.DateFilter(
        field_name='date_opened', lookup_expr='iexact')
    balance_min = django_filters.NumberFilter(
        field_name='balance', lookup_expr='gte')
    balance_max = django_filters.NumberFilter(
        field_name='balance', lookup_expr='lte')

    class Meta:
        model = Account
        fields = [
            'account_type',
            'user',
            'date_opened',
            'balance_min',
            'balance_max',
        ]
