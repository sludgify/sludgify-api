from .database import Database
from ..models import WalletUserModel, UserModel


class WalletUserDatabase(Database):
    @staticmethod
    async def insert(user_id):
        pass

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
