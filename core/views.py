from urllib.parse import unquote
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tally_client import TallyMaster, TallyVoucher
from .serializers import (
    GroupSerializer, 
    LedgerSerializer, 
    VoucherSerializer, 
    LedgerAlterSerializer
)

# Create instances of the API classes to be used across views
master_api = TallyMaster()
voucher_api = TallyVoucher()


def handle_tally_response(tally_response, action, resource_name="resource"):
    """Parses and formats Tally's XML response into a standard DRF response."""
    response_data = tally_response.get('RESPONSE', {})
    
    created = int(response_data.get('CREATED', 0))
    altered = int(response_data.get('ALTERED', 0))
    deleted = int(response_data.get('DELETED', 0))
    exceptions = int(response_data.get('EXCEPTIONS', 0))
    
    if action == "CREATE" and created > 0:
        return Response({
            "success": True,
            "message": f"✅ {resource_name} created successfully.",
            "tally_response": tally_response
        }, status=status.HTTP_201_CREATED)
    
    if action == "ALTER" and altered > 0:
        return Response({
            "success": True,
            "message": f"✅ {resource_name} altered successfully.",
            "tally_response": tally_response
        }, status=status.HTTP_200_OK)
    
    if action == "DELETE" and (deleted > 0 or altered > 0): 
        return Response({
            "success": True,
            "message": f"✅ {resource_name} deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

    if exceptions > 0:
        # Try to extract more detailed error information
        error_message = tally_response.get('ENVELOPE', {}).get('BODY', {}).get('DATA', {}).get('IMPORTRESULT', {}).get('LINEERROR', 'Data validation failed.')
        
        # For CREATE actions with exceptions, it's likely a duplicate/validation error
        if action == "CREATE":
            return Response({
                "success": False,
                "error": f"⚠️ {resource_name} already exists in TallyPrime or validation failed.",
                "suggestion": "Altering gro ups via API is not supported. Please change the parent in TallyPrime UI or delete and recreate.",
                "tally_response": tally_response
            }, status=status.HTTP_409_CONFLICT)
        
        return Response({
            "success": False,
            "error": f"❌ Tally exception: {error_message}",
            "tally_response": tally_response
        }, status=status.HTTP_409_CONFLICT)
    
    if action in ["CREATE", "ALTER"]:
        return Response({
            "success": False,
            "error": f"⚠️ Failed to {action.lower()} {resource_name}. It may already exist or was not found.",
            "tally_response": tally_response
        }, status=status.HTTP_409_CONFLICT)
    
    if action == "DELETE":
        return Response({
            "success": False,
            "error": f"⚠️ Failed to delete {resource_name}. Resource not found.",
            "tally_response": tally_response
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        "success": False,
        "error": "Unknown Tally response.",
        "tally_response": tally_response
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupView(APIView):
    """
    API endpoint to manage groups in TallyPrime.
    GET: List groups (not implemented yet)
    POST: Create a new group
    DELETE: Delete a group
    """
    
    def post(self, request):
        """Create a new group"""
        serializer = GroupSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        group_name = serializer.validated_data['group_name']
        parent_group = serializer.validated_data['parent_group']
        
        try:
            # Check if group already exists before attempting to create
            if master_api.check_group_exists(group_name):
                return Response({
                    "success": False,
                    "error": f"⚠️ Group '{group_name}' already exists in TallyPrime. Use PUT method to alter it instead.",
                    "suggestion": "Use PUT /api/groups/{group_name}/ to modify the existing group"
                }, status=status.HTTP_409_CONFLICT)
            
            tally_response = master_api.create_group(group_name, parent_group)
            return handle_tally_response(tally_response, "CREATE", f"Group '{group_name}'")
        except Exception as e:
            return Response({
                "success": False,
                "error": "An error occurred while connecting to Tally.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, name):
        """Explicitly not supported: altering groups via API."""
        return Response({
            "success": False,
            "error": "Method not allowed.",
            "message": "Altering groups via API is not supported by TallyPrime. Use Tally UI or delete and recreate.",
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def delete(self, request, name):
        """
        Delete a group by marking it as deleted in Tally.
        Optionally accepts parent_group as a query parameter or in the request body.
        """
        from urllib.parse import unquote
        name = unquote(name)
        parent_group = request.query_params.get('parent_group') or request.data.get('parent_group')

        try:
            tally_response = master_api.delete_group(name, parent_group)
            response_data = tally_response.get('RESPONSE', {})

            deleted = int(response_data.get('DELETED', 0))
            altered = int(response_data.get('ALTERED', 0))

            if deleted > 0 or altered > 0:
                return Response({
                    "success": True,
                    "message": f"✅ Group '{name}' deleted successfully from Tally.",
                    "tally_response": response_data
                }, status=status.HTTP_200_OK)

            line_error = response_data.get('LINEERROR') or tally_response.get('ENVELOPE', {}) \
                .get('BODY', {}).get('DATA', {}).get('IMPORTRESULT', {}).get('LINEERROR')

            if line_error:
                return Response({
                    "success": False,
                    "error": f"❌ Tally error: {line_error}",
                    "tally_response": tally_response
                }, status=status.HTTP_409_CONFLICT)

            return Response({
                "success": False,
                "error": f"⚠️ Failed to delete Group '{name}'. It may not exist or already be deleted.",
                "tally_response": tally_response
            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({
                "success": False,
                "error": "Connection error.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LedgerView(APIView):
    """
    API endpoint to manage ledgers in TallyPrime.
    GET: List ledgers (not implemented yet)
    POST: Create a new ledger
    PUT: Alter an existing ledger
    DELETE: Delete a ledger
    """
    
    def post(self, request):
        """Create a new ledger"""
        serializer = LedgerSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ledger_name = serializer.validated_data['ledger_name']
        parent_group = serializer.validated_data['parent_group']
        opening_balance = serializer.validated_data.get('opening_balance', 0)
        
        try:
            tally_response = master_api.create_ledger(ledger_name, parent_group, opening_balance)
            return handle_tally_response(tally_response, "CREATE", f"Ledger '{ledger_name}'")
        except Exception as e:
            return Response({
                "success": False,
                "error": "An error occurred while connecting to Tally.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, name):
        """Alter an existing ledger"""
        serializer = LedgerAlterSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tally_response = master_api.alter_ledger(
                name, 
                serializer.validated_data['new_parent_group'], 
                serializer.validated_data.get('new_opening_balance', 0.0)
            )
            return handle_tally_response(tally_response, "ALTER", f"Ledger '{name}'")
        except Exception as e:
            return Response({
                "success": False,
                "error": "Connection error.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, name):
        """Delete a ledger"""
        try:
            tally_response = master_api.delete_ledger(name)
            return handle_tally_response(tally_response, "DELETE", f"Ledger '{name}'")
        except Exception as e:
            return Response({
                "success": False,
                "error": "Connection error.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VoucherView(APIView):
    """
    API endpoint to create vouchers in TallyPrime.
    POST: Create a single voucher
    """
    
    def post(self, request):
        """Create a single voucher"""
        serializer = VoucherSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Pass as a list to the create method (it expects a list)
            tally_response = voucher_api.create([serializer.validated_data])
            response_data = tally_response.get("RESPONSE", {})
            
            created = int(response_data.get("CREATED", 0))
            altered = int(response_data.get("ALTERED", 0))
            errors = int(response_data.get("ERRORS", 0))
            exceptions = int(response_data.get("EXCEPTIONS", 0))

            if created > 0:
                return Response({
                    "success": True,
                    "message": f"✅ Voucher created successfully ({created}).",
                    "voucher_number": serializer.validated_data['voucher_number'],
                    "voucher_type": serializer.validated_data['voucher_type'],
                    "details": response_data,
                }, status=status.HTTP_201_CREATED)
            elif altered > 0:
                return Response({
                    "success": True,
                    "message": f"ℹ️ Voucher altered ({altered}).",
                    "voucher_number": serializer.validated_data['voucher_number'],
                    "details": response_data,
                }, status=status.HTTP_200_OK)
            elif errors > 0 or exceptions > 0:
                return Response({
                    "success": False,
                    "message": "❌ Tally returned an error.",
                    "details": response_data,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "success": False,
                    "message": "⚠️ No voucher created or altered. Check Tally logs.",
                    "details": response_data,
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception as e:
            return Response({
                "success": False,
                "error": f"Server/connection error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)