from flask_socketio import join_room, send, emit, disconnect
from flask import request
from ..utils import (
    AuthJwt,
    GeminiTextResponseController,
    save_markdown_to_pdf,
    GeminiAudioTranscriber,
    GeminiFileResponseController,
)
import cloudinary.uploader
from ..models import UserModel, ChatHistoryModel
from ..config import google_api_key
import datetime
import base64
import tempfile
import os


def register_socketio_events(socketio, chat_data):
    response_text = GeminiTextResponseController(google_api_key)
    audio_transcriber = GeminiAudioTranscriber(google_api_key)
    file_responder = GeminiFileResponseController(google_api_key)

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
        msg_type = data.get("type", "text")
        urls = []

        def save_and_emit(payload):
            ChatHistoryModel(
                room=room,
                original_message=payload["original_message"],
                response_message=payload["response_message"],
                links=payload["links"],
                user=data_user,
                created_at=int(datetime.datetime.now().timestamp()),
            ).save()

            if room not in chat_data:
                chat_data[room] = []
            chat_data[room].append(payload)

            emit("message_with_links", payload, room=room)

        methode = data.get("methode")
        if methode != "resume":
            if msg_type == "text":
                msg = data.get("msg")
                if msg:
                    result = response_text.get_response_text(msg)
                    full_msg = f"{'\n'.join(i.text for i in result)}"

                    try:
                        result_file = save_markdown_to_pdf(result)
                        result_cd = cloudinary.uploader.upload(result_file)
                        urls.append(result_cd["secure_url"])
                    except Exception as e:
                        print(f"Cloudinary upload error: {e}")
                        urls.append("File upload failed.")

                    payload = {
                        "username": username,
                        "original_message": msg,
                        "response_message": full_msg,
                        "links": urls,
                    }

                    save_and_emit(payload)

            elif msg_type == "voice":
                audio_base64 = data.get("audio")
                if audio_base64:
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".m4a"
                    ) as temp_audio_file:
                        audio_data = base64.b64decode(audio_base64)
                        temp_audio_file.write(audio_data)
                        temp_audio_file_path = temp_audio_file.name

                    try:
                        transcribed_result = audio_transcriber.transcribe(
                            temp_audio_file_path
                        )
                        transcribed_text = " ".join(
                            [res.text for res in transcribed_result]
                        )

                        result = response_text.get_response_text(transcribed_text)
                        full_msg = f"{'\n'.join(i.text for i in result)}"

                        try:
                            result_file = save_markdown_to_pdf(result)
                            result_cd = cloudinary.uploader.upload(result_file)
                            urls.append(result_cd["secure_url"])
                        except Exception as e:
                            print(f"Cloudinary upload error: {e}")
                            urls.append("File upload failed.")

                        payload = {
                            "username": username,
                            "original_message": transcribed_text,
                            "response_message": full_msg,
                            "links": urls,
                        }

                        save_and_emit(payload)

                    finally:
                        os.remove(temp_audio_file_path)
        elif methode == "resume":
            if msg_type == "text":
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
                    payload = {
                        "username": username,
                        "original_message": msg,
                        "response_message": full_msg,
                        "links": urls,
                    }

                    save_and_emit(payload)

                except Exception as e:
                    print(f"Error: {e}")

                finally:
                    if pdf_path and os.path.exists(pdf_path):
                        os.remove(pdf_path)
