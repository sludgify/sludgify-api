from flask_socketio import join_room, send, emit, disconnect
from flask import request
from ..utils import AuthJwt, TransactionPayment
from ..models import UserModel, TransactionPaymentModel
import time
import datetime
import threading


def register_transaction_payment_socketio_events(socketio):
    transaction_payment = TransactionPayment()

    def countdown_timer(socketio, room, seconds, unique_code):
        for remaining in range(seconds, -1, -1):
            socketio.emit(
                "countdown",
                {"remaining": remaining},
                room=room,
                namespace="/transaction-payment",
            )
            time.sleep(1)
            if remaining == 0:
                socketio.emit(
                    "transaction_expired",
                    {"unique_code": unique_code, "status": "expire"},
                    room=room,
                    namespace="/transaction-payment",
                )

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
        trx = transaction_payment.check_status_sync(unique_code)
        if trx["transaction_status"] == "pending":
            now = datetime.datetime.now(datetime.timezone.utc)
            expired_at = data_transaction_payment.expired_at

            if isinstance(expired_at, (int, float)):
                expired_at = datetime.datetime.fromtimestamp(
                    expired_at, tz=datetime.timezone.utc
                )

            countdown_seconds = int((expired_at - now).total_seconds())

            if countdown_seconds > 0:
                threading.Thread(
                    target=countdown_timer,
                    args=(socketio, room, countdown_seconds, unique_code),
                    daemon=True,
                ).start()
            else:
                socketio.emit(
                    "transaction_expired",
                    {"unique_code": unique_code, "status": "expire"},
                    room=room,
                    namespace="/transaction-payment",
                )
