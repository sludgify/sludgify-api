from .database import Database
from ..models import WalletUserModel, UserModel


class WalletUserDatabase(Database):
    @staticmethod
    async def insert(user_id, created_at):
        if user_data := UserModel.objects(id=user_id).first():
            data_wallet = WalletUserModel(
                user=user_data, created_at=created_at, updated_at=created_at
            )
            data_wallet.save()
            return data_wallet

    @staticmethod
    async def get(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "by_user_id":
            if user_data := UserModel.objects(id=user_id).first():
                if wallet_data := WalletUserModel.objects(user=user_data).first():
                    return wallet_data

    @staticmethod
    async def delete(category, **kwargs):
        pass

    @staticmethod
    async def update(category, **kwargs):
        pass
