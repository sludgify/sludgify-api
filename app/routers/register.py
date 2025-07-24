from flask import Blueprint, request
from ..controllers import RegisterController

register_router = Blueprint("register_router", __name__)
register_controller = RegisterController()


@register_router.post("/sludgify/register")
async def user_register():
    data = request.json
    timestamp = request.timestamp
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    company_name = data.get("company_name", "")
    confirm_password = data.get("confirm_password", "")
    provider = data.get("provider", "")
    token = data.get("token", "")
    return await register_controller.user_register(
        provider,
        token,
        first_name,
        last_name,
        company_name,
        email,
        password,
        confirm_password,
        timestamp,
    )
