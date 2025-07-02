from flask import Blueprint, request
from ..utils import jwt_required
from ..controllers import CarbonCreditController

carbon_credit_router = Blueprint("carbon_credit_router", __name__)
carbon_credit_controller = CarbonCreditController()


@carbon_credit_router.get("/sludgify/carbon-credit/total-credit")
@jwt_required()
async def total_carbon_credit():
    user = request.user
    return await carbon_credit_controller.total_carbon_credit(user)


@carbon_credit_router.get("/sludgify/carbon-credit/price")
@jwt_required()
async def price_carbon_credit():
    user = request.user
    return await carbon_credit_controller.price_carbon_credit(user)
