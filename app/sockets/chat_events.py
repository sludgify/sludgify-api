import deep_translator.exceptions
from flask_socketio import join_room, send, emit, disconnect
from flask import request
from ..utils import (
    AuthJwt,
    save_markdown_to_pdf,
    GeminiFileResponseController,
    GeminiESGReporter,
    Misc,
    SocketEmit,
)
import cloudinary.uploader
from ..models import UserModel, ChatHistoryModel
from ..config import google_api_key
import datetime
import os
import traceback
import deep_translator


def register_chat_bot_socketio_events(socketio, chat_data):
    response_text = GeminiESGReporter(google_api_key)
    file_responder = GeminiFileResponseController(google_api_key)

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

        methode = data.get("methode")
        if methode != "resume":
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
        elif methode == "resume":
            msg = data.get("msg")
            pdf_base64 = data.get("pdf_base64")

            def validate_and_save_pdf(base64_string: str) -> str:
                import base64
                import tempfile

                file_data = base64.b64decode(base64_string)
                if file_data[:5] != b"%PDF-":
                    raise ValueError("File bukan PDF yang valid.")

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as temp_file:
                    temp_file.write(file_data)
                    return temp_file.name

            pdf_path = None

            try:
                pdf_path = validate_and_save_pdf(pdf_base64)
                print(f"File valid disimpan di: {pdf_path}")

                result = file_responder.get_response_from_file(
                    pdf_path, "Tolong ringkas isi file ini dalam 3 kalimat."
                )

                full_msg = f"{'\n'.join(i.text for i in result)}"

                try:
                    result_file = save_markdown_to_pdf(full_msg)
                    result_cd = cloudinary.uploader.upload(result_file)
                    urls.append(result_cd["secure_url"])
                except Exception as e:
                    traceback.print_exc()
                    print(f"Cloudinary upload error: {e}")

                payload = {
                    "username": username,
                    "original_message": msg,
                    "response_message": full_msg,
                    "links": urls,
                }
                SocketEmit.chat_emit(payload, data_user, room, chat_data)

            except Exception as e:
                print(f"Error: {e}")

            finally:
                if pdf_path and os.path.exists(pdf_path):
                    os.remove(pdf_path)
