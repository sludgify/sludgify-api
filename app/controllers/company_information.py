from ..databases import CompanyInformationDatabase
from flask import jsonify, request, make_response
from ..utils import SendEmail, generate_etag
from email_validator import validate_email
from ..serializers import UserSerializer, CompanyInformationSerializer
import pycountry
from ..models import CompanyNullModel


class CompanyInformationController:
    def __init__(self):
        self.user_seliazer = UserSerializer()
        self.company_information_serializer = CompanyInformationSerializer()

    async def get_company_information(self, user):
        if not (
            user_data := await CompanyInformationDatabase.get(
                "by_user_id", user_id=user.id
            )
        ):
            company_data = self.company_information_serializer.serialize(
                CompanyNullModel()
            )
        else:
            company_data = self.company_information_serializer.serialize(user_data)

        etag = generate_etag(company_data)

        client_etag = request.headers.get("If-None-Match")
        if client_etag == etag:
            return make_response("", 304)

        response_data = {
            "data": company_data,
            "message": "successfully get user company information",
        }

        response = make_response(jsonify(response_data), 200)
        response.headers["Content-Type"] = "application/json"
        response.headers["ETag"] = etag
        return response

    async def update_company_information(
        self, user, country, position, email, phone_number, address, company_name
    ):
        errors = {}
        if country:
            if not isinstance(country, str):
                errors.setdefault("country", []).append("MUST_TEXT")
            if not (country_data := pycountry.countries.get(name=country)):
                errors.setdefault("country", []).append("IS_INVALID")
            else:
                country = f"{country_data.name}".lower()
        if position:
            if not isinstance(position, str):
                errors.setdefault("position", []).append("MUST_TEXT")
            if isinstance(position, str) and len(position) < 5:
                errors.setdefault("position", []).append("TOO_SHORT")
            if isinstance(position, str) and len(position) > 15:
                errors.setdefault("position", []).append("TOO_LONG")
        if email:
            if not isinstance(email, str):
                errors.setdefault("email", []).append("MUST_TEXT")
            try:
                valid = validate_email(email)
                email = valid.email
            except:
                errors.setdefault("email", []).append("IS_INVALID")
        if phone_number:
            if not isinstance(phone_number, str):
                errors.setdefault("phone_number", []).append("MUST_TEXT")
        if address:
            if not isinstance(address, str):
                errors.setdefault("address", []).append("MUST_TEXT")
        if company_name:
            if not isinstance(company_name, str):
                errors.setdefault("company_name", []).append("MUST_TEXT")
            if isinstance(company_name, str) and len(company_name) < 5:
                errors.setdefault("company_name", []).append("TOO_SHORT")
            if isinstance(company_name, str) and len(company_name) > 15:
                errors.setdefault("company_name", []).append("TOO_LONG")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        company_information_update = await CompanyInformationDatabase.update(
            "company_information",
            user_id=user.id,
            country=country,
            position=position,
            email=email,
            phone_number=phone_number,
            address=address,
            company_name=company_name,
        )
        SendEmail.send_email(
            "Update Company Information",
            [user.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Company Information</title>
</head>
<body>
    <p>Hello {user.email},</p>
    <p>your company has been updated</p>
</body>
</html>
                """,
        )
        user_me = self.company_information_serializer.serialize(
            company_information_update
        )
        return (
            jsonify(
                {
                    "message": "successfully update email company",
                    "data": user_me,
                }
            ),
            201,
        )
