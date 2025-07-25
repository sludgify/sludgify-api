from flask import jsonify
from ..utils import TransactionPayment
from ..serializers import TransactionPaymentSerializer
from ..databases import TransactionPaymentDatabase
from ..config import transaction_payment as TRANSACTION_PAYMENT
import datetime
import midtransclient


class TransactionPaymentController:
    def __init__(self):
        self.payment_midtrans = TransactionPayment()
        self.transaction_payment_serializer = TransactionPaymentSerializer()

    async def get_transaction_carbon_credit(self, user, unique_code):
        try:
            result = await self.payment_midtrans.check_status_async(unique_code)
        except midtransclient.error_midtrans.MidtransAPIError:
            return (
                jsonify(
                    {
                        "message": "transaction not found",
                    }
                ),
                404,
            )
        if not (
            user_data := await TransactionPaymentDatabase.get(
                "by_unique_code", unique_code=unique_code, user_id=f"{user.id}"
            )
        ):
            return (
                jsonify(
                    {
                        "message": "transaction not found",
                    }
                ),
                404,
            )
        if not result["transaction_status"] == user_data.status:
            await TransactionPaymentDatabase.update(
                "status_by_unique_code",
                unique_code=unique_code,
                user_id=f"{user.id}",
                status=result["transaction_status"],
            )
        data_transaction = self.transaction_payment_serializer.serialize(
            user_data,
        )
        return (
            jsonify(
                {
                    "message": "successfully get transaction",
                    "data": data_transaction,
                }
            ),
            200,
        )

    async def cancle_transaction_carbon_credit(self, user, unique_code):
        try:

            result = await self.payment_midtrans.check_status_async(unique_code)
        except midtransclient.error_midtrans.MidtransAPIError:
            return (
                jsonify(
                    {
                        "message": "transaction not found",
                        "errors": {"transaction": ["NOT_FOUND"]},
                    }
                ),
                404,
            )
        if not (
            user_data := await TransactionPaymentDatabase.get(
                "by_unique_code", unique_code=unique_code, user_id=f"{user.id}"
            )
        ):
            return (
                jsonify(
                    {
                        "message": "transaction not found",
                    }
                ),
                404,
            )
        if user_data.status == "cancel":
            return (
                jsonify(
                    {
                        "message": "transaction already cancle",
                    }
                ),
                409,
            )
        try:
            result = await self.payment_midtrans.cancel_transaction_async(unique_code)
        except midtransclient.error_midtrans.MidtransAPIError:
            pass
        if not result["transaction_status"] == user_data.status:
            await TransactionPaymentDatabase.update(
                "status_by_unique_code",
                unique_code=unique_code,
                user_id=f"{user.id}",
                status=result["transaction_status"],
            )
        data_transaction = self.transaction_payment_serializer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully cancle transaction",
                    "data": data_transaction,
                }
            ),
            201,
        )

    async def transaction_carbon_credit(
        self, user, amount, transaction_payment, timestamp
    ):
        errors = {}
        transaction_payment = transaction_payment.lower()
        if transaction_payment not in TRANSACTION_PAYMENT.split(", "):
            errors.setdefault("transaction_payment", []).append("IS_INVALID")
        if amount == None:
            errors.setdefault("amount", []).append("IS_REQUIRED")
        else:
            if not isinstance(amount, int):
                errors.setdefault("amount", []).append("MUST_INTEGER")
            if isinstance(amount, int) and amount < 0:
                errors.setdefault("amount", []).append("TOO_LOW")
        if errors:
            return jsonify({"errors": errors, "message": "validations error"}), 400
        unique_code = await self.payment_midtrans.create_code_async()
        created_at = int(timestamp.timestamp())
        expired_at = timestamp + datetime.timedelta(minutes=5)
        if transaction_payment == "qris":
            user_payment = await self.payment_midtrans.create_qris_async(
                unique_code, amount
            )
            user_transaction = await TransactionPaymentDatabase.insert(
                f"{user.id}",
                f"top up credit dengan saldo {amount}",
                unique_code,
                transaction_payment,
                user_payment["actions"][0]["url"],
                amount,
                created_at,
                int(expired_at.timestamp()),
            )
        elif transaction_payment == "mandiri":
            user_payment = await self.payment_midtrans.create_transfer_async(
                transaction_payment,
                unique_code,
                amount,
                {
                    "id": unique_code,
                    "price": amount,
                    "quantity": 1,
                    "name": f"top up credit sebesar {amount}",
                },
                {
                    "username": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                },
            )
            user_transaction = await TransactionPaymentDatabase.insert(
                f"{user.id}",
                f"top up credit dengan saldo {amount}",
                unique_code,
                transaction_payment,
                f'{user_payment["biller_code"]} {user_payment["bill_key"]}',
                amount,
                created_at,
                int(expired_at.timestamp()),
            )
        elif transaction_payment == "permata":
            user_payment = await self.payment_midtrans.create_transfer_async(
                transaction_payment,
                unique_code,
                amount,
                {
                    "id": unique_code,
                    "price": amount,
                    "quantity": 1,
                    "name": f"top up credit sebesar {amount}",
                },
                {
                    "username": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                },
            )
            user_transaction = await TransactionPaymentDatabase.insert(
                f"{user.id}",
                f"top up credit dengan saldo {amount}",
                unique_code,
                transaction_payment,
                f'{user_payment["permata_va_number"]}',
                amount,
                created_at,
                int(expired_at.timestamp()),
            )
        else:
            user_payment = await self.payment_midtrans.create_transfer_async(
                transaction_payment,
                unique_code,
                amount,
                {
                    "id": unique_code,
                    "price": amount,
                    "quantity": 1,
                    "name": f"top up credit sebesar {amount}",
                },
                {
                    "username": f"{user.first_name} {user.last_name}",
                    "email": user.email,
                },
            )
            user_transaction = await TransactionPaymentDatabase.insert(
                f"{user.id}",
                f"top up credit dengan saldo {amount}",
                unique_code,
                transaction_payment,
                user_payment["va_numbers"][0]["va_number"],
                amount,
                created_at,
                int(expired_at.timestamp()),
            )
        data_transaction = self.transaction_payment_serializer.serialize(
            user_transaction
        )
        if transaction_payment == "qris":
            return (
                jsonify(
                    {
                        "message": "successfully create transaction",
                        "data": data_transaction,
                    }
                ),
                201,
            )
        return (
            jsonify(
                {
                    "message": "successfully create transaction",
                    "data": data_transaction,
                }
            ),
            201,
        )
