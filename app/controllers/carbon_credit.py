from flask import jsonify
from ..databases import WalletUserDatabase


class CarbonCreditController:
    @staticmethod
    async def price_carbon_credit(user):
        return (
            jsonify(
                {
                    "message": "successfully get price carbon credit",
                    "data": {"price": 150000},
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "created_at": user.created_at,
                        "updated_at": user.updated_at,
                        "is_active": user.is_active,
                        "provider": user.provider,
                        "email": user.email,
                    },
                }
            ),
            200,
        )

    @staticmethod
    async def total_carbon_credit(user):
        user_wallet = await WalletUserDatabase.get("by_user_id", user_id=user.id)
        return (
            jsonify(
                {
                    "message": "successfully get total carbon credit",
                    "data": {
                        "id": user_wallet.id,
                        "wallet": user_wallet.wallet,
                        "created_at": user_wallet.created_at,
                        "updated_at": user_wallet.updated_at,
                    },
                    "user": {
                        "id": user_wallet.user.id,
                        "username": user_wallet.user.username,
                        "created_at": user_wallet.user.created_at,
                        "updated_at": user_wallet.user.updated_at,
                        "is_active": user_wallet.user.is_active,
                        "provider": user_wallet.user.provider,
                        "email": user_wallet.user.email,
                    },
                }
            ),
            200,
        )
