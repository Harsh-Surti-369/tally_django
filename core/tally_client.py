from datetime import datetime,date
import requests
import xmltodict
import json

TALLY_URL = "http://localhost:9000"

def send_request_to_tally(xml_request):
    """
    Sends an XML request to the TallyPrime server and returns the parsed XML response as a dictionary.
    """
    headers = {'Content-Type': 'application/xml'}
    try:
        response = requests.post(TALLY_URL, data=xml_request, headers=headers)
        response.raise_for_status()
        return xmltodict.parse(response.content)

    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to TallyPrime at {TALLY_URL}. Is the application running?")
        raise Exception(f"Connection Error: {e}")



def create_group(group_name, parent_group):
    
    xml_request = f"""<ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Import Data</TALLYREQUEST>
        </HEADER>
        
        <BODY>
            <IMPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>All Masters</REPORTNAME>
                </REQUESTDESC>
                
                <REQUEST>
                
                    <TALLYMESSAGE xmlns:UDF="TallyUDF">
                        <GROUP ACTION="Create">
                            <NAME>{group_name}</NAME>
                            <PARENT>{parent_group}</PARENT>
                        </GROUP>
                        
                    </TALLYMESSAGE>
                </REQUEST>
                
            </IMPORTDATA>
        </BODY>
        </ENVELOPE>"""
    
    return send_request_to_tally(xml_request)

def create_ledger(ledger_name, parent_group, opening_balance=0.0):
    """
    Creates a new Ledger in TallyPrime
    
    Args:
        ledger_name (str): Name of the new ledger
        parent_group (str): Parent group under which the ledger will be created
        opening_balance (float): Opening balance for the ledger (default is 0.0)
    
    Returns:
        dict: Parsed XML response from TallyPrime
    """
    
    xml_request = f"""
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Import Data</TALLYREQUEST>
        </HEADER>
        
        <BODY>
            <IMPORTDATA>          
                <REQUESTDESC>
                    <REPORTNAME>All Masters</REPORTNAME>
                </REQUESTDESC>
                <REQUESTDATA>
                    <TALLYMESSAGE>
                        <LEDGER Action="Create">
                            <NAME>{ledger_name}</NAME>
                            <PARENT>{parent_group}</PARENT>
                            <OPENINGBALANCE>{opening_balance}</OPENINGBALANCE>
                        </LEDGER>
                    </TALLYMESSAGE>
                </REQUESTDATA>
            </IMPORTDATA>
        </BODY>
    </ENVELOPE>
    """
    return send_request_to_tally(xml_request)

def create_voucher(vouchers_data):
    """
    Creates one or more Vouchers in TallyPrime based on the provided list of data.
    Generates the required XML in the correct structure, matching Tally's expectations.
    """
    all_vouchers_xml = ""
    for voucher_data in vouchers_data:
        # Format DATE as YYYYMMDD
        voucher_date = voucher_data.get('date')
        if hasattr(voucher_date, 'strftime'):
            formatted_date = voucher_date.strftime("%Y%m%d")
        else:  # accept already formatted string or int
            formatted_date = str(voucher_date)
        
        ledger_entries_xml = ""
        for entry in voucher_data.get('ledger_entries', []):
            is_deemed_positive = 'Yes' if entry.get('is_deemed_positive', False) else 'No'
            amount = abs(entry['amount']) if is_deemed_positive == 'Yes' else -abs(entry['amount'])
            ledger_entries_xml += f"""
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>{entry['ledger_name']}</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{is_deemed_positive}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{amount}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>
            """
        
        # Voucher block (one per voucher)
        all_vouchers_xml += f"""
            <VOUCHER>
                <DATE>{formatted_date}</DATE>
                <NARRATION>{voucher_data.get('narration', '')}</NARRATION>
                <VOUCHERTYPENAME>{voucher_data['voucher_type']}</VOUCHERTYPENAME>
                <VOUCHERNUMBER>{voucher_data['voucher_number']}</VOUCHERNUMBER>
                <PERSISTEDVIEW>Accounting Voucher View</PERSISTEDVIEW>
                <ISINVOICE>{"Yes" if voucher_data.get('is_invoice', False) else "No"}</ISINVOICE>
                {ledger_entries_xml}
            </VOUCHER>
        """

    # Full XML - as per Tally's Import Vouchers requirement
    xml_request = f"""
    <ENVELOPE>
        <HEADER>
            <TALLYREQUEST>Import</TALLYREQUEST>
        </HEADER>
        <BODY>
            <IMPORTDATA>
                <REQUESTDESC>
                    <REPORTNAME>Vouchers</REPORTNAME>
                </REQUESTDESC>
                <REQUESTDATA>
                    <TALLYMESSAGE xmlns:UDF="TallyUDF">
                        {all_vouchers_xml}
                    </TALLYMESSAGE>
                </REQUESTDATA>
            </IMPORTDATA>
        </BODY>
    </ENVELOPE>"""

    return send_request_to_tally(xml_request)

if __name__ == "__main__":
    # Example voucher data to create (add more vouchers to the list if needed)
    vouchers_data = [
        {
            "date": "20250914",  # Or a Python date object, e.g., datetime.date(2025, 9, 14)
            "narration": "Payment for invoice #456",
            "voucher_type": "Payment",
            "voucher_number": "101",
            "is_invoice": False,
            "ledger_entries": [
                {
                    "ledger_name": "Cash",
                    "is_deemed_positive": False,  # Cr side
                    "amount": 5000
                },
                {
                    "ledger_name": "Sales",
                    "is_deemed_positive": True,  # Dr side
                    "amount": 5000
                }
            ]
        }
    ]

    # Call the function to create voucher(s)
    response = create_voucher(vouchers_data)

    # Print the response from Tally (for debugging/logging)
    print("Tally Response:")
    print(response)

   
    
    
    # setup_essential_masters()
   
    # TEST to create a new group in Tally
    
    # print("Attempting to create a new Tally group...")
    
    # # You can change these values to test different scenarios
    # test_group_name = "My Test Group"
    # test_parent_group = "Sundry Debtors" 
    
    # try:
    #     response = create_group(test_group_name, test_parent_group)
    #     import json
        
    #     # Check Tally's response for success/failure
    #     # Tally returns a <RESPONSE> tag with <CREATED> count on success
    #     if response and 'RESPONSE' in response and 'CREATED' in response['RESPONSE']:
    #         created_count = response['RESPONSE']['CREATED']
    #         if created_count and int(created_count) > 0:
    #             print(f"✅ Success! Created {created_count} group(s).")
    #             print("Full Response (as a Python dictionary):")
    #             print(json.dumps(response, indent=2))
    #         else:
    #             print("⚠️  Connected, but Tally did not create a new group. It might already exist.")
    #             print("Full Response (as a Python dictionary):")
    #             print(json.dumps(response, indent=2))
    #     else:
    #         print("❌ Failure: Unexpected Tally response format.")
    #         print("Full Response (as a Python dictionary):")
    #         print(json.dumps(response, indent=2))
            
    # except Exception as e:
    #     print(f"❌ An error occurred: {e}")


# Test to create a new ledger in Tally
    # test_ledger_name = "Customer ABC"
    # test_ledger_parent = "Sundry Debtors" 
    # test_opening_balance = 7500.00
    
    # try:
    #     response = create_ledger(test_ledger_name, test_ledger_parent, test_opening_balance)
    #     if response and 'RESPONSE' in response and 'CREATED' in response['RESPONSE']:
    #         created_count = response['RESPONSE']['CREATED']
    #         if created_count and int(created_count) > 0:
    #             print(f"✅ Success! Created {created_count} ledger(s).")
    #             print("Full Response (as a Python dictionary):")
    #             print(json.dumps(response, indent=2))
    #         else:
    #             print("⚠️  Connected, but Tally did not create a new ledger. It might already exist.")
    #             print("Full Response (as a Python dictionary):")
    #             print(json.dumps(response, indent=2))
    #     else:
    #         print("❌ Failure: Unexpected Tally response format for ledger creation.")
    #         print("Full Response (as a Python dictionary):")
    #         print(json.dumps(response, indent=2))
            
    # except Exception as e:
    #     print(f"❌ An error occurred during ledger creation: {e}")
