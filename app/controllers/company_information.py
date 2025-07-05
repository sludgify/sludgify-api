from ..databases import CompanyInformationDatabase
from flask import jsonify
from ..utils import SendEmail
from email_validator import validate_email
from ..serializers import UserSerializer, CompanyInformationSerializer
import pycountry
from phone_number_validator.validator import PhoneNumberValidator
from ..models import CompanyNullModel


class CompanyInformationController:
    def __init__(self):
        self.user_seliazer = UserSerializer()
        self.company_information_serializer = CompanyInformationSerializer()
        self.phone_number_validator = PhoneNumberValidator(
            api_key="num_live_QyLVfWfdCvoXZKFqegBJoBLYx0MByYc9tQMEaDjQ"
        )

    async def get_company_information(self, user):
        if not (
            user_data := await CompanyInformationDatabase.get(
                "by_user_id", user_id=user.id
            )
        ):
            company_null = CompanyNullModel()
            return (
                jsonify(
                    {
                        "data": company_null,
                        "message": "successfully get company information",
                    }
                ),
                200,
            )
        company_data = self.company_information_serializer.serialize(user_data)
        return (
            jsonify(
                {
                    "data": company_data,
                    "message": "successfully get company information",
                }
            ),
            200,
        )

    async def update_email(self, user, email):
        errors = {}
        if email is None or (isinstance(email, str) and email.strip() == ""):
            errors.setdefault("email", []).append("IS_REQUIRED")
        else:
            if not isinstance(email, str):
                errors.setdefault("email", []).append("MUST_TEXT")
            try:
                valid = validate_email(email)
                email = valid.email
            except:
                errors.setdefault("email", []).append("IS_INVALID")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await CompanyInformationDatabase.update(
                "email",
                user_id=user.id,
                email=email,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update Email Company",
            [email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Email Company</title>
</head>
<body>
    <p>Hello {email},</p>
    <p>your email company has been updated to {email}</p>
</body>
</html>
                """,
        )
        user_me = self.company_information_serializer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update email company",
                    "data": user_me,
                }
            ),
            201,
        )

    async def update_country(self, user, country):
        errors = {}
        if country is None or (isinstance(country, str) and country.strip() == ""):
            errors.setdefault("country", []).append("IS_REQUIRED")
        else:
            if not isinstance(country, str):
                errors.setdefault("country", []).append("MUST_TEXT")
            if not (country_data := pycountry.countries.get(name=country)):
                errors.setdefault("country", []).append("IS_INVALID")
            else:
                country = f"{country_data.name}".lower()
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await CompanyInformationDatabase.update(
                "country",
                user_id=user.id,
                country=country,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update Country Company",
            [user.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Country Company</title>
</head>
<body>
    <p>Hello {user.email},</p>
    <p>your Country company has been updated to {country_data}</p>
</body>
</html>
                """,
        )
        user_me = self.company_information_serializer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update email company",
                    "data": user_me,
                }
            ),
            201,
        )

    async def update_position(self, user, position):
        errors = {}
        if position is None or (isinstance(position, str) and position.strip() == ""):
            errors.setdefault("position", []).append("IS_REQUIRED")
        else:
            if not isinstance(position, str):
                errors.setdefault("position", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await CompanyInformationDatabase.update(
                "position",
                user_id=user.id,
                position=position,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update Position Company",
            [user.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Position Company</title>
</head>
<body>
    <p>Hello {user.email},</p>
    <p>your Position company has been updated to {position}</p>
</body>
</html>
                """,
        )
        user_me = self.company_information_serializer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update email company",
                    "data": user_me,
                }
            ),
            201,
        )

    async def update_phone_number(self, user, phone_number):
        errors = {}
        if phone_number is None or (
            isinstance(phone_number, str) and phone_number.strip() == ""
        ):
            errors.setdefault("phone_number", []).append("IS_REQUIRED")
        else:
            if not isinstance(phone_number, str):
                errors.setdefault("phone_number", []).append("MUST_TEXT")
            if not (
                phone_number_is_valid := self.phone_number_validator.validate(
                    phone_number
                )
            ):
                errors.setdefault("phone_number", []).append("IS_INVALID")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await CompanyInformationDatabase.update(
                "phone_number", user_id=user.id, phone_number=phone_number
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update Phone Number Company Company",
            [user.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Phone Number Company Company</title>
</head>
<body>
    <p>Hello {user.email},</p>
    <p>your Phone Number Company company has been updated to {phone_number}</p>
</body>
</html>
                """,
        )
        user_me = self.company_information_serializer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update email company",
                    "data": user_me,
                }
            ),
            201,
        )
