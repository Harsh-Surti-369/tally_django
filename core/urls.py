from django.urls import path
from .views import GroupView, LedgerView, VoucherView

urlpatterns = [
    # Group endpoints
    path('groups/', GroupView.as_view(), name='group-create'),
    path('groups/<str:name>/', GroupView.as_view(), name='group-delete'),
    
    # Ledger endpoints
    path('ledgers/', LedgerView.as_view(), name='ledger-create'),
    path('ledgers/<str:name>/', LedgerView.as_view(), name='ledger-alter-delete'),
    
    # Voucher endpoints
    path('vouchers/', VoucherView.as_view(), name='voucher-create'),
]