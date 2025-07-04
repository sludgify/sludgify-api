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


@company_information_router.patch("/sludgify/company-information/country")
@jwt_required()
async def update_country():
    user = request.user
    json = request.json
    country = json.get("country", "")
    return await company_information_controller.update_country(user, country)


@company_information_router.patch("/sludgify/company-information/email")
@jwt_required()
async def update_email():
    user = request.user
    json = request.json
    email = json.get("email", "")
    return await company_information_controller.update_email(user, email)


@company_information_router.patch("/sludgify/company-information/position")
@jwt_required()
async def update_position():
    user = request.user
    json = request.json
    position = json.get("position", "")
    return await company_information_controller.update_position(user, position)


@company_information_router.patch("/sludgify/company-information/phone-number")
@jwt_required()
async def update_phone_number():
    user = request.user
    json = request.json
    phone_number = json.get("phone_number", "")
    return await company_information_controller.update_phone_number(user, phone_number)
