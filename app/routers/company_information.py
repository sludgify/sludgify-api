from flask import Blueprint, request
from ..utils import jwt_required
from ..controllers import CompanyInformationController

company_information_router = Blueprint("company_information_router", __name__)
company_information_controller = CompanyInformationController()


@company_information_router.get("/sludgify/company-information")
@jwt_required()
async def get_company_information():
    user = request.user
    return await company_information_controller.get_company_information(user)


@company_information_router.patch("/sludgify/company-information")
@jwt_required()
async def update_company_information():
    user = request.user
    forms = request.form
    country = forms.get("country", None)
    position = forms.get("position", None)
    email = forms.get("email", None)
    phone_number = forms.get("phone_number", None)
    address = forms.get("address", None)
    company_name = forms.get("company_name", None)
    return await company_information_controller.update_company_information(
        user, country, position, email, phone_number, address, company_name
    )
