from .database import Database
from ..models import ChatHistoryModel


class ChatHistoryDatabase(Database):
    @staticmethod
    async def insert(created_at, room, original_message, response_message, links, user):
        result_chat_history = ChatHistoryModel(
            room=room,
            original_message=original_message,
            response_message=response_message,
            links=links,
            user=user,
            created_at=created_at,
        )
        result_chat_history.save()
        return result_chat_history

    @staticmethod
    async def get(category, **kwargs):
        if category == "all":
            return ChatHistoryModel.objects.all()

    @staticmethod
    async def delete(category, **kwargs):
        if category == "all":
            return ChatHistoryModel.objects.delete()

    @staticmethod
    async def update(category, **kwargs):
        pass
