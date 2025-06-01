from flask import jsonify


class SludgifyAnalysisController:
    @staticmethod
    async def emission_comparison(user):
        return (
            jsonify(
                {
                    "message": "successfully get emission comparison",
                    "data": [
                        {
                            "january": 40,
                            "february": 50,
                            "march": 60,
                            "april": 70,
                            "may": 80,
                            "june": 90,
                            "july": 100,
                            "august": 100,
                            "september": 1000,
                            "october": 100,
                            "november": 60,
                            "december": 50,
                        }
                    ],
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
    async def management_summary(user):
        return (
            jsonify(
                {
                    "message": "successfully get sludge management summary",
                    "data": [
                        {
                            "january": {"b3": 40, "non_b3": 80},
                            "february": {"b3": 50, "non_b3": 90},
                            "march": {"b3": 60, "non_b3": 100},
                            "april": {"b3": 70, "non_b3": 100},
                            "may": {"b3": 80, "non_b3": 100},
                            "june": {"b3": 90, "non_b3": 100},
                            "july": {"b3": 100, "non_b3": 100},
                            "august": {"b3": 100, "non_b3": 100},
                            "september": {"b3": 100, "non_b3": 100},
                            "october": {"b3": 100, "non_b3": 100},
                            "november": {"b3": 60, "non_b3": 100},
                            "december": {"b3": 50, "non_b3": 100},
                        }
                    ],
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
    async def project_completed(user):
        return (
            jsonify(
                {
                    "message": "successfully get project completed",
                    "data": {"completed": 30, "in_progress": 5},
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
    async def total_sludge(user):
        return (
            jsonify(
                {
                    "message": "successfully get total sludge",
                    "data": {"total_sludge": 23560, "percentage": 10},
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
    async def emission_reductions(user):
        return (
            jsonify(
                {
                    "message": "successfully get co2 emission reduction",
                    "data": {"total_sludge": 4712, "percentage": 8},
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
