from flask import Blueprint, request
from ..utils import jwt_required
from ..controllers import ProfileController

profile_router = Blueprint("profile_router", __name__)
profile_controller = ProfileController()


@profile_router.get("/sludgify/default-avatar")
async def default_avatar():
    return await profile_controller.default_avatar()


@profile_router.patch("/sludgify/user/username")
@jwt_required()
async def update_username():
    user = request.user
    json = request.json
    username = json.get("username", "")
    return await profile_controller.update_username(user, username)


@profile_router.patch("/sludgify/user/password")
@jwt_required()
async def update_password():
    user = request.user
    json = request.json
    timestamp = request.timestamp
    password = json.get("password", "")
    confirm_password = json.get("confirm_password", "")
    return await profile_controller.update_password(
        user, password, confirm_password, timestamp
    )


@profile_router.patch("/sludgify/user/email")
@jwt_required()
async def update_email():
    user = request.user
    json = request.json
    timestamp = request.timestamp
    email = json.get("email", "")
    otp = json.get("otp", "")
    return await profile_controller.update_email(user, email, otp, timestamp)
