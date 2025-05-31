from flask import Blueprint, request
from ..controllers import ProfileController
from ..utils import jwt_required

me_router = Blueprint("me_router", __name__)


@me_router.get("/sludgify/@me")
@jwt_required()
async def user_login():
    user = request.user
    return await ProfileController.user_me(user)
