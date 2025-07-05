import pathlib
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

        if msg_type == "text":
            msg = data.get("msg")
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
                    result_file = save_markdown_to_pdf(result)
                    result_cd = cloudinary.uploader.upload(result_file)
                    urls.append(result_cd["secure_url"])

                    payload = {
                        "username": username,
                        "original_message": transcribed_text,
                        "response_message": full_msg,
                        "links": urls,
                    }

                    ChatHistoryModel(
                        room=room,
                        original_message=transcribed_text,
                        response_message=full_msg,
                        links=urls,
                        user=data_user,
                        created_at=int(datetime.datetime.now().timestamp()),
                    ).save()

                    if room not in chat_data:
                        chat_data[room] = []
                    chat_data[room].append(payload)

                    emit("message_with_links", payload, room=room)

                finally:
                    os.remove(temp_audio_file_path)

        elif msg_type == "resume":
            file_base64 = data.get("file")
            msg = data.get("msg", "Ringkas file berikut ini.")

            if file_base64:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as temp_pdf_file:
                    file_data = base64.b64decode(file_base64)
                    temp_pdf_file.write(file_data)
                    temp_pdf_file_path = temp_pdf_file.name

                try:
                    if msg.startswith("[voice_prompt]:"):
                        audio_base64 = msg.replace("[voice_prompt]:", "")
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
                            msg = " ".join([res.text for res in transcribed_result])
                        finally:
                            os.remove(temp_audio_file_path)

                    summarized_result = file_responder.summarize_file(
                        temp_pdf_file_path, msg
                    )
                    summarized_text = "\n".join([res.text for res in summarized_result])

                    result_file = save_markdown_to_pdf(summarized_result)
                    result_cd = cloudinary.uploader.upload(result_file)
                    urls.append(result_cd["secure_url"])

                    payload = {
                        "username": username,
                        "original_message": msg,
                        "response_message": summarized_text,
                        "links": urls,
                    }

                    ChatHistoryModel(
                        room=room,
                        original_message=msg,
                        response_message=summarized_text,
                        links=urls,
                        user=data_user,
                        created_at=int(datetime.datetime.now().timestamp()),
                    ).save()

                    if room not in chat_data:
                        chat_data[room] = []
                    chat_data[room].append(payload)

                    emit("message_with_links", payload, room=room)

                finally:
                    os.remove(temp_pdf_file_path)
