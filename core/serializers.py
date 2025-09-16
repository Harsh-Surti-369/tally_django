from rest_framework import serializers

class GroupSerializer(serializers.Serializer):
    """
    Serializer to handle data for creating a new Tally group.
    """
    group_name = serializers.CharField(max_length=255)
    parent_group = serializers.CharField(max_length=255)

class LedgerSerializer(serializers.Serializer):
    """
    Serializer to handle data for creating a new Tally ledger.
    """
    ledger_name = serializers.CharField(max_length=255)
    parent_group = serializers.CharField(max_length=255)
    opening_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    

class LedgerEntrySerializer(serializers.Serializer):
    ledger_name = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_deemed_positive = serializers.BooleanField(required=False,default=False)
    is_party_ledger = serializers.BooleanField(required=False,default=False)
    
class VoucherSerializer(serializers.Serializer):
    voucher_type = serializers.CharField(max_length=100)
    voucher_number = serializers.CharField(max_length=255)
    date = serializers.DateField(format="%Y%m%d")
    is_invoice = serializers.BooleanField(required=False,default=True)
    ledger_entries = LedgerEntrySerializer(many=True)
    
