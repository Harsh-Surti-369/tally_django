from django.urls import path,include
from .views import CreateGroupView, CreateLedgerView,CreateVoucherView

urlpatterns = [
    path('groups/create/',CreateGroupView.as_view(),name='create-group'),
    path('ledgers/create/',CreateLedgerView.as_view(),name='create-ledger'),
    path('vouchers/create/',CreateVoucherView.as_view(),name='create-voucher'),
    ]