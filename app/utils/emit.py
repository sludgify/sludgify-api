from flask_socketio import emit
import datetime
from ..models import ChatHistoryModel


class SocketEmit:
    def chat_emit(payload, data_user, room, chat_data):
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
