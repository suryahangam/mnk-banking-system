from django.urls import path
from .views import (TransactionCreateView, ListTransactionView,
                    DetailTransactionView, CurrencyConverterView)


urlpatterns = [
    path('create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('list/', ListTransactionView.as_view(), name='transaction-list'),
    path('<int:pk>/detail', DetailTransactionView.as_view(),
         name='transaction-detail'),
    path('currency-converter/', CurrencyConverterView.as_view(),
         name='currency-converter'),
]
