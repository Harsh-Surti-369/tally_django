from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .tally_client import TallyMaster, TallyVoucher
from .serializers import GroupSerializer, LedgerSerializer, VoucherSerializer

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
                            "success": True,
                            "message": f"Group '{group_name}' created successfully in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            "success": False,
                            "error": "Failed to create group. It might already exist.",
                            "tally_response": tally_response
                        }, status=status.HTTP_409_CONFLICT)
                else:
                    return Response({
                        "success": False,
                        "error": "Unexpected response from Tally.",
                        "tally_response": tally_response
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            except Exception as e:
                return Response({
                    "success": False,
                    "error": "An error occurred while connecting to Tally.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
                            "success": True,
                            "message": f"Ledger '{ledger_name}' created successfully in Tally.",
                            "tally_response": tally_response
                        }, status=status.HTTP_201_CREATED)
                    else:
                        return Response({
                            "success": False,
                            "error": "Failed to create ledger. It might already exist.",
                            "tally_response": tally_response
                        }, status=status.HTTP_409_CONFLICT)
                else:
                    return Response({
                        "success": False,
                        "error": "Unexpected response from Tally.",
                        "tally_response": tally_response
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({
                    "success": False,
                    "error": "An error occurred while connecting to Tally.",
                    "details": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CreateVoucher(APIView):
    """
    API endpoint to create a single voucher in TallyPrime.
    """
    def post(self, request):
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
                    "message": f"Voucher created successfully ({created}).",
                    "voucher_number": serializer.validated_data['voucher_number'],
                    "voucher_type": serializer.validated_data['voucher_type'],
                    "details": response_data,
                }, status=status.HTTP_201_CREATED)
            elif altered > 0:
                return Response({
                    "success": True,
                    "message": f"Voucher altered ({altered}).",
                    "voucher_number": serializer.validated_data['voucher_number'],
                    "details": response_data,
                }, status=status.HTTP_200_OK)
            elif errors > 0 or exceptions > 0:
                return Response({
                    "success": False,
                    "message": "Tally returned an error.",
                    "details": response_data,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "success": False,
                    "message": "No voucher created or altered. Check Tally logs.",
                    "details": response_data,
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception as e:
            return Response({
                "success": False,
                "error": f"Server/connection error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateVoucherBatch(APIView):
    """
    API endpoint to create multiple vouchers in TallyPrime.
    """
    def post(self, request):
        serializer = VoucherSerializer(data=request.data, many=True)
        
        if not serializer.is_valid():
            return Response({
                "success": False,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Pass the list directly
            tally_response = voucher_api.create(serializer.validated_data)
            response_data = tally_response.get("RESPONSE", {})
            
            created = int(response_data.get("CREATED", 0))
            altered = int(response_data.get("ALTERED", 0))
            errors = int(response_data.get("ERRORS", 0))
            exceptions = int(response_data.get("EXCEPTIONS", 0))
            total_vouchers = len(serializer.validated_data)

            if created > 0:
                return Response({
                    "success": True,
                    "message": f"Created {created} out of {total_vouchers} vouchers.",
                    "created_count": created,
                    "total_requested": total_vouchers,
                    "details": response_data,
                }, status=status.HTTP_201_CREATED)
            elif altered > 0:
                return Response({
                    "success": True,
                    "message": f"Altered {altered} vouchers.",
                    "altered_count": altered,
                    "total_requested": total_vouchers,
                    "details": response_data,
                }, status=status.HTTP_200_OK)
            elif errors > 0 or exceptions > 0:
                return Response({
                    "success": False,
                    "message": "Tally returned errors.",
                    "errors": errors,
                    "exceptions": exceptions,
                    "details": response_data,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    "success": False,
                    "message": "No vouchers created or altered. Check Tally logs.",
                    "details": response_data,
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        except Exception as e:
            return Response({
                "success": False,
                "error": f"Server/connection error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)