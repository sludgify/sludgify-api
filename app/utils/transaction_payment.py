import time
import random
import string
import midtransclient
import datetime
from ..config import server_key, client_key


class TransactionPayment:
    def __init__(self):
        self.api = midtransclient.CoreApi(
            is_production=False,
            server_key=server_key,
            client_key=client_key,
        )

    async def parse_rupiah(self, formatted):
        nilai_str = formatted.replace("Rp ", "")
        nilai_str = nilai_str.replace(",", "").replace(".", "")
        nilai_str = nilai_str[:-2] + "." + nilai_str[-2:]
        nilai = float(nilai_str)
        if nilai.is_integer():
            nilai = int(nilai)
        return nilai

    async def create_code_async(self):
        timestamp = int(time.time())
        random_string = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=6)
        )
        transaction_code = f"TX{timestamp}{random_string}"
        return transaction_code

    async def check_status_async(self, unique_code):
        transaction_status = self.api.transactions.status(unique_code)
        return transaction_status

    def check_status_sync(self, unique_code):
        transaction_status = self.api.transactions.status(unique_code)
        return transaction_status

    async def cancel_transaction_async(self, unique_code):
        cancel_response = self.api.transactions.cancel(unique_code)
        return cancel_response

    async def create_qris_async(self, unique_code, amount):
        order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S +0700")
        params = {
            "payment_type": "gopay",
            "transaction_details": {
                "order_id": unique_code,
                "gross_amount": amount,
            },
            "custom_expiry": {
                "order_time": order_time,
                "expiry_duration": 5,
                "unit": "minute",
            },
        }
        transaction = self.api.charge(params)
        return transaction

    async def create_transfer_async(
        self, bank, unique_code, amount, item_details, customer_details
    ):
        if bank == "permata":
            params = {
                "payment_type": bank,
                "transaction_details": {
                    "order_id": unique_code,
                    "gross_amount": amount,
                },
            }
        elif bank == "mandiri":
            params = {
                "payment_type": "echannel",
                "transaction_details": {
                    "order_id": unique_code,
                    "gross_amount": amount,
                },
                "item_details": [
                    item_details,
                ],
                "echannel": {
                    "bill_info1": "Payment:",
                    "bill_info2": item_details["name"],
                },
                "customer_details": customer_details,
            }
        else:
            params = {
                "payment_type": "bank_transfer",
                "transaction_details": {
                    "order_id": unique_code,
                    "gross_amount": amount,
                },
                "item_details": [
                    item_details,
                ],
                "bank_transfer": {
                    "bank": bank,
                },
                "customer_details": customer_details,
            }
        transaction = self.api.charge(params)
        return transaction
