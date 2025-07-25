from .chat_events import *


def register_socket_io(socket_io, chat_data):
    register_chat_bot_socketio_events(socket_io, chat_data)
