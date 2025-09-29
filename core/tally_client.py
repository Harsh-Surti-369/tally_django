from datetime import datetime, date
import requests
import xmltodict
import json

class TallyClient:
    """
    Base client for all Tally API requests.
    Handles the core request/response logic.
    """
    TALLY_URL = "http://localhost:9000"

    def _send_request_to_tally(self, xml_request):
        """
        Sends an XML request to the TallyPrime server and returns the parsed XML response as a dictionary.
        This method is for internal use.
        """
        headers = {'Content-Type': 'application/xml'}
        try:
            response = requests.post(self.TALLY_URL, data=xml_request, headers=headers)
            response.raise_for_status()
            # Tally can return a single string in some error cases, handle that here.
            if response.text.startswith("<"):
                return xmltodict.parse(response.content)
            return {"RESPONSE": response.text}

        except requests.exceptions.RequestException as e:
            print(f"Error: Could not connect to TallyPrime at {self.TALLY_URL}. Is the application running?")
            raise Exception(f"Connection Error: {e}")

class TallyMaster(TallyClient):
    """
    A class for general Master-related operations (Ledgers, Groups, etc.).
    """
    def create_group(self, group_name, parent_group):
        """
        Creates a new Group master in TallyPrime.
        """
        xml_request = f"""<ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Import Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <IMPORTDATA>
                    <REQUESTDESC>
                        <REPORTNAME>All Masters</REPORTNAME>
                    </REQUESTDESC>
                    <REQUESTDATA>
                        <TALLYMESSAGE xmlns:UDF="TallyUDF">
                            <GROUP ACTION="Create">
                                <NAME>{group_name}</NAME>
                                <PARENT>{parent_group}</PARENT>
                            </GROUP>
                        </TALLYMESSAGE>
                    </REQUESTDATA>
                </IMPORTDATA>
            </BODY>
            </ENVELOPE>"""
        return self._send_request_to_tally(xml_request)


    def create_ledger(self, ledger_name, parent_group, opening_balance=0.0):
        """
        Creates a new Ledger master in TallyPrime.
        """
        xml_request = f"""<ENVELOPE>
            <HEADER>
                <TALLYREQUEST>Import Data</TALLYREQUEST>
            </HEADER>
            <BODY>
                <IMPORTDATA>
                    <REQUESTDESC>
                        <REPORTNAME>All Masters</REPORTNAME>
                    </REQUESTDESC>
                    <REQUESTDATA>
                        <TALLYMESSAGE xmlns:UDF="TallyUDF">
                            <LEDGER Action="Create">
                                <NAME>{ledger_name}</NAME>
                                <PARENT>{parent_group}</PARENT>
                                <OPENINGBALANCE>{opening_balance}</OPENINGBALANCE>
                            </LEDGER>
                        </TALLYMESSAGE>
                    </REQUESTDATA>
                </IMPORTDATA>
            </BODY>
        </ENVELOPE>"""
        return self._send_request_to_tally(xml_request)

class TallyVoucher(TallyClient):
    """
    A class for all Voucher-related operations.
    """
    def _format_date(self, date_value):
        """
        Convert various date formats to YYYYMMDD format required by Tally.
        Handles: date objects, datetime objects, and string formats.
        """
        print(f"DEBUG: Input date value: {date_value}, type: {type(date_value)}")
        
        if isinstance(date_value, datetime):
            result = date_value.strftime("%Y%m%d")
            print(f"DEBUG: Formatted datetime to: {result}")
            return result
        elif isinstance(date_value, date):
            result = date_value.strftime("%Y%m%d")
            print(f"DEBUG: Formatted date to: {result}")
            return result
        elif isinstance(date_value, str):
            # Try to parse if it's a string
            for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%Y%m%d"):
                try:
                    parsed_date = datetime.strptime(date_value, fmt)
                    result = parsed_date.strftime("%Y%m%d")
                    print(f"DEBUG: Parsed string '{date_value}' with format '{fmt}' to: {result}")
                    return result
                except ValueError:
                    continue
            # If no format matched, assume it's already in YYYYMMDD format
            print(f"DEBUG: Using string as-is: {date_value}")
            return date_value
        else:
            raise ValueError(f"Unsupported date format: {type(date_value)}")

    def create(self, vouchers_data):
        """
        Creates one or more Vouchers in TallyPrime based on the provided list of data.
        """
        all_vouchers_xml = ""
        
        for idx, voucher_data in enumerate(vouchers_data):
            print(f"\n=== Processing Voucher {idx + 1} ===")
            print(f"Raw voucher data: {voucher_data}")
            
            # Format the date properly
            formatted_date = self._format_date(voucher_data.get('date'))
            print(f"Final formatted date: {formatted_date}")
            
            ledger_entries_xml = ""
            for entry in voucher_data.get('ledger_entries', []):
                is_deemed_positive = 'Yes' if entry.get('is_deemed_positive', False) else 'No'
                amount = float(entry['amount'])
                
                ledger_entries_xml += f"""
                <ALLLEDGERENTRIES.LIST>
                    <LEDGERNAME>{entry['ledger_name']}</LEDGERNAME>
                    <ISDEEMEDPOSITIVE>{is_deemed_positive}</ISDEEMEDPOSITIVE>
                    <AMOUNT>{amount}</AMOUNT>
                </ALLLEDGERENTRIES.LIST>"""
            
            voucher_xml = f"""
            <VOUCHER>
                <GUID></GUID>
                <DATE>{formatted_date}</DATE>
                <VOUCHERTYPENAME>{voucher_data['voucher_type']}</VOUCHERTYPENAME>
                <VOUCHERNUMBER>{voucher_data['voucher_number']}</VOUCHERNUMBER>
                <NARRATION>{voucher_data.get('narration', '')}</NARRATION>
                <PARTYLEDGERNAME></PARTYLEDGERNAME>
                {ledger_entries_xml}
            </VOUCHER>"""
            
            all_vouchers_xml += voucher_xml

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

        print(f"\n{'='*60}")
        print("FINAL XML REQUEST:")
        print(f"{'='*60}")
        print(xml_request)
        print(f"{'='*60}\n")

        return self._send_request_to_tally(xml_request)

if __name__ == "__main__":
    client = TallyClient()
    master_api = TallyMaster()
    voucher_api = TallyVoucher()

    # Pre-create a few ledgers for our test vouchers
    try:
        master_api.create_ledger("Conveyance", "Indirect Expenses")
        master_api.create_ledger("Bank of India", "Bank Accounts")
        master_api.create_ledger("Cash", "Cash-in-hand")
    except Exception as e:
        print(f"Error during ledger creation: {e}")

    # Test data for a batch of vouchers
    vouchers_data = [
        {
            'date': '20250913',
            'voucher_type': 'Payment',
            'voucher_number': 'PMT-001',
            'narration': 'Payment for conveyance expenses.',
            'is_invoice': False,
            'ledger_entries': [
                {'ledger_name': 'Conveyance', 'amount': 500.00, 'is_deemed_positive': True},
                {'ledger_name': 'Bank of India', 'amount': -500.00, 'is_deemed_positive': False}
            ]
        },
        {
            'date': '20250914',
            'voucher_type': 'Payment',
            'voucher_number': 'PMT-002',
            'narration': 'Payment for fuel.',
            'is_invoice': False,
            'ledger_entries': [
                {'ledger_name': 'Conveyance', 'amount': 750.00, 'is_deemed_positive': True},
                {'ledger_name': 'Bank of India', 'amount': -750.00, 'is_deemed_positive': False}
            ]
        }
    ]

    try:
        response = voucher_api.create(vouchers_data)
        print("\nFinal Tally Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"An error occurred during voucher creation: {e}")