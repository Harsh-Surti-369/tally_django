from rest_framework import serializers
from datetime import datetime

class GroupSerializer(serializers.Serializer):
    """
    Serializer to handle data for creating a new Tally group.
    """
    group_name = serializers.CharField(max_length=255)
    parent_group = serializers.CharField(max_length=255)

class DeleteGroupSerializer(serializers.Serializer):
    """
    Serializer to handle data for deleting a Tally group.
    """
    group_name = serializers.CharField(max_length=255)

class LedgerSerializer(serializers.Serializer):
    """
    Serializer to handle data for creating a new Tally ledger.
    """
    ledger_name = serializers.CharField(max_length=255)
    parent_group = serializers.CharField(max_length=255)
    opening_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    

class LedgerEntrySerializer(serializers.Serializer):
    ledger_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_deemed_positive = serializers.BooleanField(default=False)

class VoucherSerializer(serializers.Serializer):
    date = serializers.DateField(format="%Y%m%d", input_formats=["%Y%m%d", "%Y-%m-%d", "%d-%b-%Y"]) 
    voucher_type = serializers.CharField()
    voucher_number = serializers.CharField()
    narration = serializers.CharField(required=False, allow_blank=True)
    is_invoice = serializers.BooleanField(default=False)
    ledger_entries = LedgerEntrySerializer(many=True)