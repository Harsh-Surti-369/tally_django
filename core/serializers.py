from rest_framework import serializers
from datetime import datetime

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
    ledger_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_deemed_positive = serializers.BooleanField( default=False)

class FlexibleDateField(serializers.DateField):
    def to_internal_value(self, value):
        # try multiple formats
        for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%Y%m%d"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        self.fail("invalid", format="YYYY-MM-DD or DD-MMM-YYYY or YYYYMMDD")

class VoucherSerializer(serializers.Serializer):
    date = FlexibleDateField()
    voucher_type = serializers.CharField()
    voucher_number = serializers.CharField()
    narration = serializers.CharField(required=False, allow_blank=True)
    is_invoice = serializers.BooleanField(default=False)
    ledger_entries = LedgerEntrySerializer(many=True)
