import deep_translator.exceptions
from flask_socketio import join_room, send, emit, disconnect
from flask import request
from ..utils import (
    AuthJwt,
    save_markdown_to_pdf,
    GeminiFileCitationController,
    GeminiESGReporter,
    Misc,
    SocketEmit,
)
import cloudinary.uploader
from ..models import UserModel, ChatHistoryModel
from ..config import google_api_key
import base64
import os
import traceback
import deep_translator
import tempfile


def register_chat_bot_socketio_events(socketio, chat_data):
    response_text = GeminiESGReporter(google_api_key)
    file_responder = GeminiFileCitationController(google_api_key)

    @socketio.on("connect", namespace="/chat-bot")
    def handle_connect():
        print(f"User connected from IP: {request.remote_addr}")

    @socketio.on("disconnect", namespace="/chat-bot")
    def handle_disconnect():
        print(f"User disconnected from IP: {request.remote_addr}")

    @socketio.on("join", namespace="/chat-bot")
    def handle_join(data):
        token = data.get("token")
        if not token:
            disconnect()
            return

        user = AuthJwt.verify_token_sync(token)
        if not user:
            disconnect()
            return

        data_user = UserModel.objects(id=user.get("sub")).first()
        if not data_user:
            disconnect()
            return

        room = f"{data_user.id}"
        username = f"{data_user.first_name} {data_user.last_name}"
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

    @socketio.on("message", namespace="/chat-bot")
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

        room = f"{data_user.id}"
        username = f"{data_user.first_name} {data_user.last_name}"
        urls = []

        method = data.get("method")
        if method != "resume":
            msg = data.get("msg")
            if msg:
                try:
                    response_text.generate_report(msg)
                    if response_text.response:
                        result = response_text._add_citations()

                        try:
                            result_file = save_markdown_to_pdf(result)
                            result_cd = cloudinary.uploader.upload(result_file)
                            urls.append(result_cd["secure_url"])
                        except Exception as e:
                            print(f"Cloudinary upload error: {e}")

                        payload = {
                            "username": username,
                            "original_message": msg,
                            "response_message": result,
                            "links": urls,
                        }
                        SocketEmit.chat_emit(payload, data_user, room, chat_data)
                except TypeError:
                    try:
                        country = Misc.get_country_code(data_user.country)
                        result_country = country if country else "en"
                        result_message = Misc.translator(
                            "mohon maaf, saya tidak dapat menjawab pertanyaan ini.",
                            result_country,
                        )
                    except deep_translator.exceptions.LanguageNotSupportedException:
                        result_message = "Sorry, I can't answer this question."
                    payload = {
                        "username": username,
                        "original_message": msg,
                        "response_message": result_message,
                        "links": urls,
                    }
                    SocketEmit.chat_emit(payload, data_user, room, chat_data)
        elif method == "resume":
            msg = data.get("msg")
            pdf_base64_list = data.get("pdf_base64_list", [])
            urls = []

            def validate_and_save_pdf(base64_string: str) -> str | None:
                try:
                    file_data = base64.b64decode(base64_string)
                    if file_data[:5] != b"%PDF-":
                        return None
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".pdf"
                    ) as temp_file:
                        temp_file.write(file_data)
                        return temp_file.name
                except Exception as e:
                    return None

            temp_files = []

            try:
                for base64_str in pdf_base64_list:
                    if base64_str.strip():
                        file_path = validate_and_save_pdf(base64_str)
                        if file_path:
                            temp_files.append(file_path)

                if not temp_files:
                    SocketEmit.chat_emit(
                        {
                            "username": username,
                            "original_message": msg,
                            "response_message": "Tidak ada file PDF valid untuk diringkas.",
                            "links": [],
                        },
                        data_user,
                        room,
                        chat_data,
                    )
                    return

                result = file_responder.get_response_text(
                    file_paths=temp_files,
                    prompt="Tolong ringkas isi file ini dalam 3 kalimat.",
                )

                full_msg = result.strip()

                try:
                    result_file = save_markdown_to_pdf(full_msg)
                    result_cd = cloudinary.uploader.upload(result_file)
                    urls.append(result_cd["secure_url"])
                except Exception as e:
                    traceback.print_exc()
                    print(f"[Cloudinary Upload Error] {e}")

                payload = {
                    "username": username,
                    "original_message": msg,
                    "response_message": full_msg,
                    "links": urls,
                }

                SocketEmit.chat_emit(payload, data_user, room, chat_data)

            except Exception as e:
                SocketEmit.chat_emit(
                    {
                        "username": username,
                        "original_message": msg,
                        "response_message": f"Terjadi kesalahan saat meresume file: {e}",
                        "links": [],
                    },
                    data_user,
                    room,
                    chat_data,
                )

            finally:
                for path in temp_files:
                    if path and os.path.exists(path):
                        os.remove(path)
