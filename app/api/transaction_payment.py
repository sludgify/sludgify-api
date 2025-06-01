from flask import Blueprint, request
from ..utils import jwt_required
from ..controllers import TransactionPaymentController

transaction_payment_router = Blueprint("transaction_payment_router", __name__)


@transaction_payment_router.post(
    "/sludgify/transaction/carbon-credit/<string:transaction_payment>"
)
@jwt_required()
async def transaction_carbon_credit(transaction_payment):
    user = request.user
    timestamp = request.timestamp
    json = request.json
    amount = json.get("amount", None)
    return await TransactionPaymentController.transaction_carbon_credit(
        user, amount, transaction_payment, timestamp
    )


@transaction_payment_router.delete(
    "/sludgify/transaction/carbon-credit/<string:unique_code>"
)
@jwt_required()
async def cancle_transaction_carbon_credit(unique_code):
    user = request.user
    return await TransactionPaymentController.cancle_transaction_carbon_credit(
        user, unique_code
    )


@transaction_payment_router.get(
    "/sludgify/transaction/carbon-credit/<string:unique_code>"
)
@jwt_required()
async def get_transaction_carbon_credit(unique_code):
    user = request.user
    return await TransactionPaymentController.get_transaction_carbon_credit(
        user, unique_code
    )
