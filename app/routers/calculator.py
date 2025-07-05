from flask import Blueprint, request
from ..utils import jwt_required
from ..controllers import CalculatorController

calculator_router = Blueprint("calculator_router", __name__)
calculator_controller = CalculatorController()


@calculator_router.get("/sludgify/carbon-emissions/calculator")
@jwt_required()
async def calculator():
    json = request.json
    massa = json.get("massa", None)
    sludge_type = json.get("sludge_type", None)
    return await calculator_controller.calculator("default", massa, sludge_type)
