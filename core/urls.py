from django.urls import path,include
from .views import CreateGroupView, CreateLedgerView, CreateVoucher

urlpatterns = [
    path('groups/create/',CreateGroupView.as_view(),name='create-group'),
    path('ledgers/create/',CreateLedgerView.as_view(),name='create-ledger'),
    path('vouchers/create/',CreateVoucher.as_view(),name='create-voucher'),
    ]