from flask import Blueprint, request
from ..controllers import ChatBotController
from ..utils import jwt_required

chat_bot_router = Blueprint("chat_bot_router", __name__)
chat_bot_controller = ChatBotController()


@chat_bot_router.delete("/sludgify/chat-bot")
@jwt_required()
async def user_login():
    return await chat_bot_controller.clear_history()


@chat_bot_router.post("/sludgify/chat-bot/message")
@jwt_required()
async def send_message():
    user = request.user
    timestamp = request.timestamp
    json = request.json
    message = json.get("message", "")
    return await chat_bot_controller.send_message(user, message, timestamp)
