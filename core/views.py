from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tally_client import create_group, create_ledger, create_voucher
from .serializers import GroupSerializer, LedgerSerializer, VoucherSerializer

# Create your views here.

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
                tally_response = create_group(group_name, parent_group)
                
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
    

class CreateLedgerView(APIView):
    """
    API endpoint to create a new ledger in TallyPrime.
    """
    
    def post(self,request):
        serializer = LedgerSerializer(data=request.data)
        
        if serializer.is_valid():
            ledger_name = serializer.validated_data['ledger_name']
            parent_group = serializer.validated_data['parent_group']
            opening_balance = serializer.validated_data.get('opening_balance', 0) # used get for optional field
            
            try:
                tally_response = create_ledger(ledger_name,parent_group,opening_balance)
                
                # check for tally response
                
                if tally_response and 'RESPONSE' in tally_response and 'CREATED' in tally_response['RESPONSE']:
                    created_count = tally_response['RESPONSE']['CREATED']
                    
                    if created_count and int(created_count) > 0:
                        return Response({
                            "message": f"Ledger '{ledger_name}' created successfully in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            "error": "Failed to create ledger. might already exist",
                            "tally_response": tally_response
                            },status=status.HTTP_409_CONFLICT)
                else:
                    return Response({
                        "error": "Unexpected response from Tally.",
                        "tally_response": tally_response
                        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({
                    "error": "An error occured while connecting to tally.",
                    "details" : str(e)
                    },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CreateVoucherView(APIView):
    def post(self, request):
        serializer = VoucherSerializer(data=request.data)
        if serializer.is_valid():
            voucher_data = serializer.validated_data

            try:
                tally_response = create_voucher(voucher_data)

                if tally_response and 'RESPONSE' in tally_response and 'CREATED' in tally_response['RESPONSE']:
                    created_count = tally_response['RESPONSE']['CREATED']
                    if created_count and int(created_count) > 0:
                        return Response({
                            "message": f"Voucher '{voucher_data['voucher_number']}' created successfully in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            "error": "Failed to create voucher. It might already exist.",
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