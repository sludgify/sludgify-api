from .database import Database
from ..models import TransactionPaymentModel, UserModel


class TransactionPaymentDatabase(Database):
    @staticmethod
    async def insert(user_id, description, unique_code, amount, created_at, expired_at):
        if user_data := UserModel.objects(id=user_id).first():
            transaction_payment_data = TransactionPaymentModel(
                user=user_data,
                description=description,
                amount=amount,
                unique_code=unique_code,
                created_at=created_at,
                expired_at=expired_at,
            )
            transaction_payment_data.save()
            return transaction_payment_data

    @staticmethod
    async def get(category, **kwargs):
        unique_code = kwargs.get("unique_code")
        user_id = kwargs.get("user_id")
        if category == "by_unique_code":
            if user_data := UserModel.objects(id=user_id).first():
                if transaction_payment_data := TransactionPaymentModel.objects(
                    unique_code=unique_code, user=user_data
                ).first():
                    return transaction_payment_data

    @staticmethod
    async def delete(category, **kwargs):
        pass

    @staticmethod
    async def update(category, **kwargs):
        unique_code = kwargs.get("unique_code")
        user_id = kwargs.get("user_id")
        if category == "is_cancle":
            if user_data := UserModel.objects(id=user_id).first():
                if transaction_payment_data := TransactionPaymentModel.objects(
                    unique_code=unique_code, user=user_data
                ).first():
                    transaction_payment_data.is_remove = True
                    transaction_payment_data.save()
                    return transaction_payment_data
