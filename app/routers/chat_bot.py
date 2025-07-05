from flask import Blueprint
from ..controllers import ChatBotController
from ..utils import jwt_required

chat_bot_router = Blueprint("chat_bot_router", __name__)
chat_bot_controller = ChatBotController()


@chat_bot_router.delete("/sludgify/chat-bot")
@jwt_required()
async def user_login():
    return await chat_bot_controller.clear_history()
