from django.urls import path
from accounts.views import (
    AccountCreateView, AccountUpdateView, AccountListView, AccountDetailView)

urlpatterns = [
    path('create-account/', AccountCreateView.as_view(), name='create_account'),
    path('<int:pk>/update-account/',
         AccountUpdateView.as_view(), name='update_account'),
    path('list-accounts/', AccountListView.as_view(),
         name='list_accounts'),  # For listing
    path('<int:pk>/account-detail/', AccountDetailView.as_view(), name='account_detail')
]
