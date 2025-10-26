from django.urls import path
from .views import CreateGroupView, DeleteGroupView, CreateLedgerView, CreateVoucherView

urlpatterns = [
    path('groups/create/', CreateGroupView.as_view(), name='create-group'),
    path('groups/delete/', DeleteGroupView.as_view(), name='delete-group'),
    path('ledgers/create/', CreateLedgerView.as_view(), name='create-ledger'),
    path('vouchers/create/', CreateVoucherView.as_view(), name='create-voucher'),
]