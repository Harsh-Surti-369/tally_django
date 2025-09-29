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
    opening_balance = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        required=False
    )


class LedgerEntrySerializer(serializers.Serializer):
    """
    Serializer for individual ledger entries within a voucher.
    """
    ledger_name = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    is_deemed_positive = serializers.BooleanField(default=False, required=False)


class FlexibleDateField(serializers.Field):
    """
    Custom date field that accepts multiple input formats and converts to Python date object.
    """
    def to_internal_value(self, value):
        """Convert string date to Python date object"""
        if isinstance(value, datetime):
            return value.date()
        
        # Try multiple date formats
        date_formats = [
            "%Y-%m-%d",      # 2025-09-30
            "%d-%b-%Y",      # 30-Sep-2025
            "%Y%m%d",        # 20250930
            "%d/%m/%Y",      # 30/09/2025
            "%m/%d/%Y",      # 09/30/2025
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(value), fmt)
                return parsed_date.date()
            except (ValueError, TypeError):
                continue
        
        raise serializers.ValidationError(
            f"Date format not recognized. Use YYYY-MM-DD, DD-MMM-YYYY, or YYYYMMDD. Got: {value}"
        )
    
    def to_representation(self, value):
        """Convert date object to string for output"""
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        elif hasattr(value, 'strftime'):
            return value.strftime("%Y-%m-%d")
        return str(value)


class VoucherSerializer(serializers.Serializer):
    """
    Serializer for creating vouchers in Tally.
    """
    date = FlexibleDateField()
    voucher_type = serializers.CharField(max_length=50)
    voucher_number = serializers.CharField(max_length=50)
    narration = serializers.CharField(required=False, allow_blank=True, default="")
    is_invoice = serializers.BooleanField(default=False, required=False)
    ledger_entries = LedgerEntrySerializer(many=True)
    
    def validate_ledger_entries(self, value):
        """
        Validate that there are at least 2 ledger entries and amounts balance.
        """
        if len(value) < 2:
            raise serializers.ValidationError(
                "A voucher must have at least 2 ledger entries (debit and credit)."
            )
        
        # Check if amounts balance (sum should be close to 0)
        total = sum(float(entry['amount']) for entry in value)
        if abs(total) > 0.01:  # Allow small floating point differences
            raise serializers.ValidationError(
                f"Ledger entries must balance. Current sum: {total}"
            )
        
        return value