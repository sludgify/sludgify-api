from flask_socketio import join_room, send, emit, disconnect
from flask import request
from ..utils import AuthJwt, GeminiTextResponseController, save_markdown_to_pdf
import cloudinary.uploader
from ..models import UserModel, ChatHistoryModel
from ..config import google_api_key
import datetime


def register_socketio_events(socketio, chat_data):
    response_text = GeminiTextResponseController(google_api_key)

    @socketio.on("connect")
    def handle_connect():
        print(f"User connected from IP: {request.remote_addr}")

    @socketio.on("disconnect")
    def handle_disconnect():
        print(f"User disconnected from IP: {request.remote_addr}")

    @socketio.on("join")
    def handle_join(data):
        token = data.get("token")
        user = AuthJwt.verify_token_sync(token)
        if not user:
            disconnect()
            return

        data_user = UserModel.objects(id=user.get("sub")).first()
        if not data_user:
            disconnect()
            return

        username = f"{data_user.first_name} {data_user.last_name}"
        room = data.get("room", "default")
        join_room(room)

        history = ChatHistoryModel.objects(room=room).order_by("created_at")
        chat_list = []
        for chat in history:
            chat_list.append(
                {
                    "username": f"{chat.user.first_name} {chat.user.last_name}",
                    "original_message": chat.original_message,
                    "response_message": chat.response_message,
                    "links": chat.links,
                }
            )

        emit("chat_history", chat_list, room=request.sid)
        send(f"{username} joined the room.", room=room)

    @socketio.on("message")
    def handle_message(data):
        token = data.get("token", "")
        user = AuthJwt.verify_token_sync(token)
        if not user:
            disconnect()
            return

        data_user = UserModel.objects(id=user.get("sub")).first()
        if not data_user:
            disconnect()
            return

        username = f"{data_user.first_name} {data_user.last_name}"
        room = data.get("room", "default")
        msg = data.get("msg")
        urls = []

        if msg:
            result = response_text.get_response_text(msg)
            full_msg = f"{'\n'.join(i.text for i in result)}"
            result_file = save_markdown_to_pdf(result)
            result_cd = cloudinary.uploader.upload(result_file)
            urls.append(result_cd["secure_url"])

            payload = {
                "username": username,
                "original_message": msg,
                "response_message": full_msg,
                "links": urls,
            }

            ChatHistoryModel(
                room=room,
                original_message=msg,
                response_message=full_msg,
                links=urls,
                user=data_user,
                created_at=int(datetime.datetime.now().timestamp()),
            ).save()

            if room not in chat_data:
                chat_data[room] = []
            chat_data[room].append(payload)

            emit("message_with_links", payload, room=room)
