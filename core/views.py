from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tally_client import TallyMaster, TallyVoucher
from .serializers import GroupSerializer, DeleteGroupSerializer, LedgerSerializer, VoucherSerializer

# Create instances of the API classes to be used across views
master_api = TallyMaster()
voucher_api = TallyVoucher()

class CreateGroupView(APIView):
    """
    API endpoint to create a new group in TallyPrime.
    """
    def post(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group_name = serializer.validated_data['group_name']
            parent_group = serializer.validated_data['parent_group']
            
            try:
                tally_response = master_api.create_group(group_name, parent_group)
                
                if tally_response and 'RESPONSE' in tally_response and 'CREATED' in tally_response['RESPONSE']:
                    created_count = tally_response['RESPONSE']['CREATED']
                    if created_count and int(created_count) > 0:
                        return Response({
                            "message": f"Group '{group_name}' created successfully in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            "error": "Failed to create group. It might already exist.",
                            "tally_response": tally_response
                        }, status=status.HTTP_409_CONFLICT)
                else:
                    return Response({
                        "error": "Unexpected response from Tally.",
                        "tally_response": tally_response
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Exception as e:
                return Response({
                    "error": "An error occurred while connecting to Tally.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteGroupView(APIView):
    """
    API endpoint to delete an existing group in TallyPrime.
    """
    def delete(self, request):
        serializer = DeleteGroupSerializer(data=request.data)
        if serializer.is_valid():
            group_name = serializer.validated_data['group_name']
            
            try:
                tally_response = master_api.delete_group(group_name)
                
                if tally_response and 'RESPONSE' in tally_response:
                    # Check for ALTERED count (Tally uses ALTERED for deletions)
                    altered_count = tally_response['RESPONSE'].get('ALTERED', 0)
                    
                    if altered_count and int(altered_count) > 0:
                        return Response({
                            "message": f"Group '{group_name}' deleted successfully from Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            "error": f"Failed to delete group '{group_name}'. It might not exist or may have dependent ledgers.",
                            "tally_response": tally_response
                        }, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({
                        "error": "Unexpected response from Tally.",
                        "tally_response": tally_response
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Exception as e:
                return Response({
                    "error": "An error occurred while connecting to Tally.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateLedgerView(APIView):
    """
    API endpoint to create a new ledger in TallyPrime.
    """
    def post(self, request):
        serializer = LedgerSerializer(data=request.data)
        if serializer.is_valid():
            ledger_name = serializer.validated_data['ledger_name']
            parent_group = serializer.validated_data['parent_group']
            opening_balance = serializer.validated_data.get('opening_balance', 0)
            
            try:
                tally_response = master_api.create_ledger(ledger_name, parent_group, opening_balance)
                
                if tally_response and 'RESPONSE' in tally_response and 'CREATED' in tally_response['RESPONSE']:
                    created_count = tally_response['RESPONSE']['CREATED']
                    if created_count and int(created_count) > 0:
                        return Response({
                            "message": f"Ledger '{ledger_name}' created successfully in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            "error": "Failed to create ledger. It might already exist.",
                            "tally_response": tally_response
                        }, status=status.HTTP_409_CONFLICT)
                else:
                    return Response({
                        "error": "Unexpected response from Tally.",
                        "tally_response": tally_response
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({
                    "error": "An error occurred while connecting to Tally.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateVoucherView(APIView):
    """
    API endpoint to create a batch of vouchers in TallyPrime.
    """
    def post(self, request):
        # We expect a list of vouchers, so many=True is needed
        serializer = VoucherSerializer(data=request.data, many=True)
        
        if serializer.is_valid():
            vouchers_data = serializer.validated_data
            
            try:
                tally_response = voucher_api.create(vouchers_data)
                
                if tally_response and 'ENVELOPE' in tally_response and 'BODY' in tally_response['ENVELOPE']:
                    import_result = tally_response['ENVELOPE']['BODY']['DATA']['IMPORTRESULT']
                    
                    created = int(import_result.get('CREATED', 0))
                    altered = int(import_result.get('ALTERED', 0))
                    exceptions = int(import_result.get('EXCEPTIONS', 0))
                    
                    if created > 0:
                        return Response({
                            "message": f"Successfully created {created} voucher(s) in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_201_CREATED)
                    elif altered > 0:
                         return Response({
                            "message": f"Successfully altered {altered} voucher(s) in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_200_OK)
                    elif exceptions > 0:
                        return Response({
                            "error": f"Tally reported {exceptions} exceptions. Check the response for details.",
                            "tally_response": tally_response
                        }, status=status.HTTP_409_CONFLICT)
                    else:
                        return Response({
                            "error": "Tally did not create or alter any vouchers. They may already exist.",
                            "tally_response": tally_response
                        }, status=status.HTTP_409_CONFLICT)
                else:
                    return Response({
                        "error": "Unexpected response from Tally.",
                        "tally_response": tally_response
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Exception as e:
                return Response({
                    "error": "An error occurred while connecting to Tally.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)