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
    Simplified version for creating vouchers with minimal XML structure
    """
    all_vouchers_xml = ""
    
    for voucher_data in vouchers_data:
        # Format DATE as DD-MMM-YYYY
        voucher_date = voucher_data.get('date')
        if hasattr(voucher_date, 'strftime'):
            formatted_date = voucher_date.strftime("%d-%b-%Y")
        else:
            formatted_date = str(voucher_date)
        
        # Build ledger entries
        ledger_entries_xml = ""
        for entry in voucher_data.get('ledger_entries', []):
            is_deemed_positive = 'Yes' if entry.get('is_deemed_positive', False) else 'No'
            amount = abs(float(entry['amount'])) if is_deemed_positive == 'Yes' else -abs(float(entry['amount']))
            
            ledger_entries_xml += f"""
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>{entry['ledger_name']}</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{is_deemed_positive}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{amount}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>"""
        
        # Simple voucher structure
        voucher_xml = f"""
            <VOUCHER VCHTYPE="{voucher_data['voucher_type']}" ACTION="Create">
                <DATE>{formatted_date}</DATE>
                <NARRATION>{voucher_data.get('narration', '')}</NARRATION>
                <VOUCHERTYPENAME>{voucher_data['voucher_type']}</VOUCHERTYPENAME>
                <VOUCHERNUMBER>{voucher_data['voucher_number']}</VOUCHERNUMBER>{ledger_entries_xml}
            </VOUCHER>"""
        
        all_vouchers_xml += voucher_xml

    # Simplified XML structure
    xml_request = f"""<ENVELOPE>
    <HEADER>
        <TALLYREQUEST>Import Data</TALLYREQUEST>
    </HEADER>
    <BODY>
        <IMPORTDATA>
            <REQUESTDESC>
                <REPORTNAME>Vouchers</REPORTNAME>
            </REQUESTDESC>
            <REQUESTDATA>
                <TALLYMESSAGE xmlns:UDF="TallyUDF">{all_vouchers_xml}
                </TALLYMESSAGE>
            </REQUESTDATA>
        </IMPORTDATA>
    </BODY>
</ENVELOPE>"""

    return send_request_to_tally(xml_request)

if __name__ == "__main__":
    vouchers_data = [
        {
            'date': '02-Apr-2025', 
            'voucher_type': 'Journal',
            'voucher_number': '10',
            'narration': 'Test voucher entry',
            'is_invoice': False,
            'ledger_entries': [
                {
                    'ledger_name': 'Cash',
                    'amount': 10000,
                    'is_deemed_positive': True
                },
                {
                    'ledger_name': 'Sales',
                    'amount': 10000,
                    'is_deemed_positive': False
                }
            ]
        }
    ]
    
    response = create_voucher(vouchers_data)
    
    print(json.dumps(response, indent=2))