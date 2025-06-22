from flask import jsonify
from ..databases import WalletUserDatabase
from ..serializers import UserSerializer


class CarbonCreditController:
    def __init__(self):
        self.user_seliazer = UserSerializer()

    async def price_carbon_credit(self, user):
        user_me = self.user_seliazer.serialize(user)
        return (
            jsonify(
                {
                    "message": "successfully get price carbon credit",
                    "data": {"price": 150000},
                    "user": user_me,
                }
            ),
            200,
        )

    async def total_carbon_credit(self, user):
        user_wallet = await WalletUserDatabase.get("by_user_id", user_id=user.id)
        user_me = self.user_seliazer.serialize(user)
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
                    "user": user_me,
                }
            ),
            200,
        )
