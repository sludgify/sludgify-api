from ..databases import ChatHistoryDatabase
from flask import jsonify


class ChatBotController:
    def __init__(self):
        pass

    async def clear_history(self):
        if not (chat_history := await ChatHistoryDatabase.get("all")):
            return jsonify({"message": "chat history not found"}), 404
        await ChatHistoryDatabase.delete("all")
        return jsonify({"message": "successfully clear chat history"}), 201
