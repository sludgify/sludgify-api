from flask import jsonify
from ..serializers import UserSerializer


class SludgifyAnalysisController:
    def __init__(self):
        self.user_serializer = UserSerializer()

    async def emission_comparison(self, user):
        user_me = self.user_serializer.serialize(user)
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
                    "user": user_me,
                }
            ),
            200,
        )

    async def management_summary(self, user):
        user_me = self.user_serializer.serialize(user)
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
                    "user": user_me,
                }
            ),
            200,
        )

    async def project_completed(self, user):
        user_me = self.user_serializer.serialize(user)
        return (
            jsonify(
                {
                    "message": "successfully get project completed",
                    "data": {"completed": 30, "in_progress": 5},
                    "user": user_me,
                }
            ),
            200,
        )

    async def total_sludge(self, user):
        user_me = self.user_serializer.serialize(user)
        return (
            jsonify(
                {
                    "message": "successfully get total sludge",
                    "data": {"total_sludge": 23560, "percentage": 10},
                    "user": user_me,
                }
            ),
            200,
        )

    @staticmethod
    async def emission_reductions(user):
        user_me = UserSerializer.serialize(user)
        return (
            jsonify(
                {
                    "message": "successfully get co2 emission reduction",
                    "data": {"total_sludge": 4712, "percentage": 8},
                    "user": user_me,
                }
            ),
            200,
        )
