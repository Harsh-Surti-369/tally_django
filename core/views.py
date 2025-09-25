# from django.shortcuts import render
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from .tally_client import create_group, create_ledger, create_voucher
# from .serializers import GroupSerializer, LedgerSerializer, VoucherSerializer

# # Create your views here.

# class CreateGroupView(APIView):
#     """
#     API endpoint to create a new group in TallyPrime.
#     """
    
#     def post(self, request):
#         serializer = GroupSerializer(data=request.data)
        
#         if serializer.is_valid():
#             group_name = serializer.validated_data['group_name']
#             parent_group = serializer.validated_data['parent_group']
            
#             try:
#                 tally_response = create_group(group_name, parent_group)
                
#                 if tally_response and 'RESPONSE' in tally_response and 'CREATED' in tally_response['RESPONSE']:
#                     created_count = tally_response['RESPONSE']['CREATED']
#                     if created_count and int(created_count) > 0:
#                         return Response({
#                             "message": f"Group '{group_name}' created successfully in Tally.",
#                             "tally_response": tally_response
#                         }, status=status.HTTP_201_CREATED)
#                     else:
#                         return Response({
#                             "error": "Failed to create group. It might already exist.",
#                             "tally_response": tally_response
#                         }, status=status.HTTP_409_CONFLICT)
#                 else:
#                     return Response({
#                         "error": "Unexpected response from Tally.",
#                         "tally_response": tally_response
#                     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
#             except Exception as e:
#                  return Response({
#                     "error": "An error occurred while connecting to Tally.",
#                     "details": str(e)
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# class CreateLedgerView(APIView):
#     """
#     API endpoint to create a new ledger in TallyPrime.
#     """
    
#     def post(self,request):
#         serializer = LedgerSerializer(data=request.data)
        
#         if serializer.is_valid():
#             ledger_name = serializer.validated_data['ledger_name']
#             parent_group = serializer.validated_data['parent_group']
#             opening_balance = serializer.validated_data.get('opening_balance', 0) # used get for optional field
            
#             try:
#                 tally_response = create_ledger(ledger_name,parent_group,opening_balance)
                
#                 # check for tally response
                
#                 if tally_response and 'RESPONSE' in tally_response and 'CREATED' in tally_response['RESPONSE']:
#                     created_count = tally_response['RESPONSE']['CREATED']
                    
#                     if created_count and int(created_count) > 0:
#                         return Response({
#                             "message": f"Ledger '{ledger_name}' created successfully in Tally.",
#                             "tally_response": tally_response
#                         }, status=status.HTTP_201_CREATED)
#                     else:
#                         return Response({
#                             "error": "Failed to create ledger. might already exist",
#                             "tally_response": tally_response
#                             },status=status.HTTP_409_CONFLICT)
#                 else:
#                     return Response({
#                         "error": "Unexpected response from Tally.",
#                         "tally_response": tally_response
#                         },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             except Exception as e:
#                 return Response({
#                     "error": "An error occured while connecting to tally.",
#                     "details" : str(e)
#                     },status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class CreateVoucher(APIView):
#     def post(self, request):
#         serializer = VoucherSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             tally_response = create_voucher([serializer.validated_data])
#             response_data = tally_response.get("RESPONSE", {})

#             created = int(response_data.get("CREATED", 0))
#             altered = int(response_data.get("ALTERED", 0))
#             errors = int(response_data.get("ERRORS", 0))
#             exceptions = int(response_data.get("EXCEPTIONS", 0))

#             if created > 0:
#                 return Response(
#                     {
#                         "message": f"✅ Voucher created successfully ({created}).",
#                         "details": response_data,
#                     },
#                     status=status.HTTP_201_CREATED,
#                 )
#             elif altered > 0:
#                 return Response(
#                     {
#                         "message": f"ℹ️ Voucher altered ({altered}).",
#                         "details": response_data,
#                     },
#                     status=status.HTTP_200_OK,
#                 )
#             elif errors > 0 or exceptions > 0:
#                 return Response(
#                     {
#                         "message": "❌ Tally returned an error.",
#                         "details": response_data,
#                     },
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#             else:
#                 return Response(
#                     {
#                         "message": "⚠️ No voucher created or altered. Check Tally logs.",
#                         "details": response_data,
#                     },
#                     status=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                 )

#         except Exception as e:
#             return Response(
#                 {"error": f"Server/connection error: {str(e)}"},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

# # class CreateVoucherView(APIView):
# #     """
# #     API to create a single voucher in TallyPrime
# #     """
# #     def convert_date_format(self, voucher_data):
# #         """Convert date from YYYY-MM-DD to DD-MMM-YYYY format"""
# #         from datetime import datetime
        
# #         if isinstance(voucher_data['date'], str):
# #             try:
# #                 date_obj = datetime.strptime(str(voucher_data['date']), "%Y-%m-%d")
# #                 voucher_data['date'] = date_obj.strftime("%d-%b-%Y")
# #             except:
# #                 pass  # Keep original if conversion fails
# #         return voucher_data
    
# #     def post(self, request):
# #         serializer = VoucherSerializer(data=request.data)
        
# #         if serializer.is_valid():
# #             voucher_data = serializer.validated_data
            
# #             # Convert date format before sending to Tally
# #             voucher_data = self.convert_date_format(voucher_data)
# #             voucher_list = [voucher_data]  # Convert to list for your function
            
# #             try:
# #                 tally_response = create_voucher(voucher_list)
                
# #                 # Check if voucher was created successfully
# #                 if (tally_response and 'RESPONSE' in tally_response and 
# #                     'CREATED' in tally_response['RESPONSE']):
# #                     created_count = tally_response['RESPONSE']['CREATED']
                    
# #                     if created_count and int(created_count) > 0:
# #                         return Response({
# #                             "success": True,
# #                             "message": f"Successfully created voucher '{serializer.validated_data['voucher_number']}'",
# #                             "voucher_number": serializer.validated_data['voucher_number'],
# #                             "voucher_type": serializer.validated_data['voucher_type'],
# #                             "created_count": int(created_count)
# #                         }, status=status.HTTP_201_CREATED)
# #                     else:
# #                         return Response({
# #                             "success": False,
# #                             "error": "Voucher was not created. Check the response for details.",
# #                             "tally_response": tally_response
# #                         }, status=status.HTTP_409_CONFLICT)
# #                 else:
# #                     return Response({
# #                         "success": False,
# #                         "error": "Unexpected response from Tally",
# #                         "tally_response": tally_response
# #                     }, status=status.HTTP_400_BAD_REQUEST)
                    
# #             except Exception as e:
# #                 return Response({
# #                     "success": False,
# #                     "error": "Error connecting to Tally",
# #                     "details": str(e)
# #                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# #         return Response({
# #             "success": False,
# #             "error": "Validation failed",
# #             "details": serializer.errors
# #         }, status=status.HTTP_400_BAD_REQUEST)


# # class CreateVoucherBatchView(APIView):
# #     """
# #     API to create multiple vouchers in TallyPrime
# #     """
# #     def convert_date_format(self, voucher_data):
# #         """Convert date from YYYY-MM-DD to DD-MMM-YYYY format"""
# #         from datetime import datetime
        
# #         if isinstance(voucher_data['date'], str):
# #             try:
# #                 date_obj = datetime.strptime(str(voucher_data['date']), "%Y-%m-%d")
# #                 voucher_data['date'] = date_obj.strftime("%d-%b-%Y")
# #             except:
# #                 pass  # Keep original if conversion fails
# #         return voucher_data
    
# #     def post(self, request):
# #         serializer = VoucherSerializer(data=request.data, many=True)
        
# #         if serializer.is_valid():
# #             vouchers_data = serializer.validated_data
            
# #             # Convert date format for each voucher
# #             for i, voucher in enumerate(vouchers_data):
# #                 vouchers_data[i] = self.convert_date_format(voucher)
            
# #             try:
# #                 tally_response = create_voucher(vouchers_data)
                
# #                 # Check if vouchers were created successfully
# #                 if (tally_response and 'RESPONSE' in tally_response and 
# #                     'CREATED' in tally_response['RESPONSE']):
# #                     created_count = tally_response['RESPONSE']['CREATED']
# #                     total_vouchers = len(vouchers_data)
                    
# #                     if created_count and int(created_count) > 0:
# #                         return Response({
# #                             "success": True,
# #                             "message": f"Successfully created {created_count} out of {total_vouchers} vouchers",
# #                             "created_count": int(created_count),
# #                             "total_requested": total_vouchers,
# #                             "voucher_numbers": [v['voucher_number'] for v in vouchers_data]
# #                         }, status=status.HTTP_201_CREATED)
# #                     else:
# #                         return Response({
# #                             "success": False,
# #                             "error": "No vouchers were created. Check the response for details.",
# #                             "tally_response": tally_response
# #                         }, status=status.HTTP_409_CONFLICT)
# #                 else:
# #                     return Response({
# #                         "success": False,
# #                         "error": "Unexpected response from Tally",
# #                         "tally_response": tally_response
# #                     }, status=status.HTTP_400_BAD_REQUEST)
                    
# #             except Exception as e:
# #                 return Response({
# #                     "success": False,
# #                     "error": "Error connecting to Tally",
# #                     "details": str(e)
# #                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# #         return Response({
# #             "success": False,
# #             "error": "Validation failed",
# #             "details": serializer.errors
# #         }, status=status.HTTP_400_BAD_REQUEST)

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

class CreateVoucher(APIView):
    def post(self, request):
        serializer = VoucherSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            tally_response = voucher_api.create([serializer.validated_data])
            response_data = tally_response.get("RESPONSE", {})
            
            created = int(response_data.get("CREATED", 0))
            altered = int(response_data.get("ALTERED", 0))
            errors = int(response_data.get("ERRORS", 0))
            exceptions = int(response_data.get("EXCEPTIONS", 0))

            if created > 0:
                return Response(
                    {
                        "message": f"✅ Voucher created successfully ({created}).",
                        "details": response_data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            elif altered > 0:
                return Response(
                    {
                        "message": f"ℹ️ Voucher altered ({altered}).",
                        "details": response_data,
                    },
                    status=status.HTTP_200_OK,
                )
            elif errors > 0 or exceptions > 0:
                return Response(
                    {
                        "message": "❌ Tally returned an error.",
                        "details": response_data,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    {
                        "message": "⚠️ No voucher created or altered. Check Tally logs.",
                        "details": response_data,
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

        except Exception as e:
            return Response(
                {"error": f"Server/connection error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
