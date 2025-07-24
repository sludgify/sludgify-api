from ..models import ChatHistoryModel
from .interfaces import SerializerInterface


class ChatHistorySerializer(SerializerInterface):
    def serialize(
        self,
        chat_hostory: ChatHistoryModel,
        id_is_null: bool = False,
        room_is_null: bool = False,
        original_message_is_null: bool = False,
        response_message_is_null: bool = False,
        created_at_is_null: bool = False,
    ) -> dict:
        data = {}
        if not id_is_null:
            data["id"] = str(chat_hostory.id) if chat_hostory.id else None
        if not room_is_null:
            data["room"] = chat_hostory.room
        if not original_message_is_null:
            data["original_message"] = chat_hostory.original_message
        if not response_message_is_null:
            data["response_message"] = chat_hostory.response_message
        if not created_at_is_null:
            data["created_at"] = chat_hostory.created_at
        return data
