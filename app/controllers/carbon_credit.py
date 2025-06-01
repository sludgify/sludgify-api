from flask import jsonify


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
        return (
            jsonify(
                {
                    "message": "successfully get total carbon credit",
                    "data": {"credit": 100},
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
