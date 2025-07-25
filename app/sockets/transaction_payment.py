from flask_socketio import join_room, send, emit, disconnect
from flask import request
from ..utils import (
    AuthJwt,
)
from ..models import UserModel, TransactionPaymentModel


def register_transaction_payment_socketio_events(socketio):
    @socketio.on("connect", namespace="/transaction-payment")
    def handle_connect():
        print(f"User connected from IP: {request.remote_addr}")

    @socketio.on("disconnect", namespace="/transaction-payment")
    def handle_disconnect():
        print(f"User disconnected from IP: {request.remote_addr}")

    @socketio.on("join", namespace="/transaction-payment")
    def handle_join(data):
        token = data.get("token")
        unique_code = data.get("unique_code")
        if not token:
            disconnect()
            return

        user = AuthJwt.verify_token_sync(token)
        if not user:
            disconnect()
            return

        data_user = UserModel.objects(id=user.get("sub")).first()
        if not data_user:
            disconnect()
            return

        if not (
            data_transaction_payment := TransactionPaymentModel.objects(
                user=data_user, unique_code=unique_code
            ).first()
        ):
            disconnect()
            return

        room = f"transaction-{data_transaction_payment.unique_code}"
        join_room(room)
