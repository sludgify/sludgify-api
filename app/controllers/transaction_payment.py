from flask import jsonify
from ..utils import TransactionPayment
from ..databases import TransactionPaymentDatabase
from ..config import transaction_payment as TRANSACTION_PAYMENT
import datetime
import midtransclient
from ..serializers import UserSerializer


class TransactionPaymentController:
    def __init__(self):
        self.user_seliazer = UserSerializer()

    async def get_transaction_carbon_credit(self, user, unique_code):
        try:
            payment_midtrans = TransactionPayment()
            result = await payment_midtrans.check_status(unique_code)
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
        user_me = self.user_seliazer.serialize(user)
        return (
            jsonify(
                {
                    "message": "successfully get transaction",
                    "data": {
                        "unique_code": user_data.unique_code,
                        "amount": user_data.amount,
                        "created_at": user_data.created_at,
                        "expired_at": user_data.expired_at,
                        "description": user_data.description,
                        "status": result["transaction_status"],
                    },
                    "user": user_me,
                }
            ),
            200,
        )

    async def cancle_transaction_carbon_credit(self, user, unique_code):
        try:
            payment_midtrans = TransactionPayment()
            result = await payment_midtrans.check_status(unique_code)
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
        if user_data.is_remove:
            return (
                jsonify(
                    {
                        "message": "transaction already cancle",
                    }
                ),
                409,
            )
        await TransactionPaymentDatabase.update(
            "is_cancle",
            unique_code=unique_code,
            user_id=f"{user.id}",
        )
        result = await payment_midtrans.cancel_transaction(unique_code)
        user_me = self.user_seliazer.serialize(user)
        return (
            jsonify(
                {
                    "message": "successfully cancle transaction",
                    "data": {
                        "unique_code": user_data.unique_code,
                        "amount": user_data.amount,
                        "created_at": user_data.created_at,
                        "expired_at": user_data.expired_at,
                        "description": user_data.description,
                        "status": result["transaction_status"],
                    },
                    "user": user_me,
                }
            ),
            201,
        )

    async def transaction_carbon_credit(
        self, user, amount, transaction_payment, timestamp
    ):
        payment_midtrans = TransactionPayment()
        errors = {}
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
            return jsonify({"errors": errors, "message": "invalid data"}), 400
        unique_code = await payment_midtrans.create_code()
        created_at = int(timestamp.timestamp())
        expired_at = timestamp + datetime.timedelta(minutes=5)
        user_transaction = await TransactionPaymentDatabase.insert(
            f"{user.id}",
            f"top up credit dengan saldo {amount}",
            unique_code,
            amount,
            created_at,
            int(expired_at.timestamp()),
        )
        user_me = self.user_seliazer.serialize(user)
        if transaction_payment == "qris":
            user_payment = await payment_midtrans.create_qris(unique_code, amount)
        elif transaction_payment == "bca":
            user_payment = await payment_midtrans.create_transfer(
                "bca",
                unique_code,
                amount,
                {
                    "id": unique_code,
                    "price": amount,
                    "quantity": 1,
                    "name": f"top up credit sebesar {amount}",
                },
                {"username": user.username, "email": user.email},
            )
        if transaction_payment == "qris":
            return (
                jsonify(
                    {
                        "message": "successfully create transaction",
                        "data": {
                            "unique_code": user_transaction.unique_code,
                            "amount": amount,
                            "created_at": user_transaction.created_at,
                            "expired_at": user_transaction.expired_at,
                            "description": user_transaction.description,
                        },
                        "payment": {
                            "url_qris": user_payment["actions"][0]["url"],
                            "transaction_id": user_payment["transaction_id"],
                            "expiry_time": user_payment["expiry_time"],
                            "status": user_payment["transaction_status"],
                        },
                        "user": user_me,
                    }
                ),
                201,
            )
        elif transaction_payment == "bca":
            return (
                jsonify(
                    {
                        "message": "successfully create transaction",
                        "data": {
                            "unique_code": user_transaction.unique_code,
                            "amount": amount,
                            "created_at": user_transaction.created_at,
                            "expired_at": user_transaction.expired_at,
                            "description": user_transaction.description,
                        },
                        "payment": {
                            "va_number": user_payment["va_numbers"][0]["va_number"],
                            "order_id": user_payment["order_id"],
                            "expiry_time": user_payment["expiry_time"],
                            "status": user_payment["transaction_status"],
                        },
                        "user": user_me,
                    }
                ),
                201,
            )
