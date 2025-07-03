from flask_socketio import join_room, send, emit, disconnect
from flask import request
from ..utils import AuthJwt, GeminiTextResponseController
import markdown
from weasyprint import HTML
import io
import cloudinary.uploader


def register_socketio_events(socketio, chat_data):
    response_text = GeminiTextResponseController(
        "AIzaSyCznQt8mB2TEvU0_wPUpWDVJHK6XanZmUg"
    )

    def save_markdown_to_pdf(responses):
        combined_text = "\n\n".join(resp.text for resp in responses)
        html_content = markdown.markdown(combined_text)
        pdf_buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(target=pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer

    @socketio.on("join")
    def handle_join(data):
        token = data.get("token")
        user = AuthJwt.verify_token_sync(token)
        if not user:
            disconnect()
            return

        username = user.get("username", "Anonymous")
        room = data.get("room", "default")
        join_room(room)

        if room not in chat_data:
            chat_data[room] = []

        emit("chat_history", chat_data[room], room=request.sid)
        send(f"{username} joined the room.", room=room)

    @socketio.on("message")
    def handle_message(data):
        token = data.get("token", "dsadsadsa")
        user = AuthJwt.verify_token_sync(token)
        print(user)
        if not user:
            disconnect()
            return

        username = user.get("username", "Anonymous")
        room = data.get("room", "default")
        msg = data.get("msg")
        urls = []

        if msg:
            result = response_text.get_response_text(msg)
            full_msg = f"{'\n'.join(i.text for i in result)}"
            result_file = save_markdown_to_pdf(result)
            result_cd = cloudinary.uploader.upload(
                result_file,
            )
            urls.append(result_cd["secure_url"])
            payload = {"username": username, "message": full_msg, "links": urls}
            if room not in chat_data:
                chat_data[room] = []
            chat_data[room].append(payload)
            emit("message_with_links", payload, room=room)
