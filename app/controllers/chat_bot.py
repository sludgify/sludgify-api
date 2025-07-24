from ..databases import ChatHistoryDatabase
from flask import jsonify
from ..utils import save_markdown_to_pdf, GeminiESGReporter
from ..config import google_api_key
import cloudinary.uploader
from ..extensions import socket_io
from ..serializers import ChatHistorySerializer


class ChatBotController:
    def __init__(self):
        self.chat_history_serializer = ChatHistorySerializer()
        self.response_text = GeminiESGReporter(google_api_key)

    async def send_message(self, user, message, timestamp):
        room = f"{user.id}"
        errors = {}
        if message is None or (isinstance(message, str) and message.strip() == ""):
            errors.setdefault("message", []).append("IS_REQUIRED")
        else:
            if not isinstance(message, str):
                errors.setdefault("message", []).append("MUST_TEXT")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        self.response_text.generate_report(message)
        if self.response_text.response:
            result = self.response_text.add_citations()
            urls = []
            try:
                result_file = save_markdown_to_pdf(result)
                result_cd = cloudinary.uploader.upload(result_file)
                urls.append(result_cd["secure_url"])
            except Exception as e:
                pass

            payload = {
                "username": f"{user.first_name} {user.last_name}",
                "original_message": message,
                "response_message": result,
                "links": urls,
            }
            result_chat_history = await ChatHistoryDatabase.insert(
                int(timestamp.timestamp()),
                room,
                message,
                result,
                urls,
                user,
            )
            socket_io.emit("message_with_links", payload)
            chat_data = self.chat_history_serializer.serialize(result_chat_history)
            return (
                jsonify({"data": chat_data, "message": "successfully send message"}),
                201,
            )

    async def clear_history(self):
        if not (chat_history := await ChatHistoryDatabase.get("all")):
            return jsonify({"message": "chat history not found"}), 404
        await ChatHistoryDatabase.delete("all")
        return jsonify({"message": "successfully clear chat history"}), 201
