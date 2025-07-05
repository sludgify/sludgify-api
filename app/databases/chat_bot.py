from .database import Database
from ..models import ChatHistoryModel


class ChatHistoryDatabase(Database):
    @staticmethod
    async def insert():
        pass

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
