import datetime
from ..models import (
    AccountActiveModel,
    ResetPasswordModel,
    OtpEmailModel,
    TransactionPaymentModel,
)
from celery.schedules import crontab, schedule
from ..utils import TransactionPayment
from ..extensions import socket_io


def register_tasks(celery_app):
    @celery_app.task(name="update_data_every_5_minutes")
    def update_data_every_5_minutes():
        expired_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())

        for model, name in [
            (AccountActiveModel, "account active"),
            (ResetPasswordModel, "reset password"),
            (OtpEmailModel, "otp email"),
        ]:
            for data in model.objects.all():
                if getattr(data, "expired_at", 0) <= expired_at or getattr(
                    data.user, "is_active", False
                ):
                    data.delete()
                    print(f"success delete token {name} {data.user.email}")

        return "success check all token"

    @celery_app.task(name="update_payment_status")
    def update_payment_status():

        transaction_payment = TransactionPayment()
        for data in TransactionPaymentModel.objects(status="pending").all():
            try:
                data_transaction = transaction_payment.check_status_sync(
                    data.unique_code
                )
            except:
                continue
            if data_transaction["transaction_status"] == "settlement":
                data.status = "settlement"
                data.save()
                socket_io.emit(
                    "transaction_status_updated",
                    {"unique_code": data.unique_code, "status": "settlement"},
                    room=f"transaction-{data.unique_code}",
                    namespace="/transaction-payment",
                )
                print(
                    f"payment settlement {data.unique_code}, user : {data.user.email}"
                )
                continue
            if data_transaction["transaction_status"] == "expire":
                data.status = "expire"
                data.save()
                socket_io.emit(
                    "transaction_status_updated",
                    {"unique_code": data.unique_code, "status": "expire"},
                    room=f"transaction-{data.unique_code}",
                    namespace="/transaction-payment",
                )
                print(f"payment expire {data.unique_code}, user : {data.user.email}")
                continue

        return "success check all payment status"

    celery_app.conf.beat_schedule = {
        "run-every-5-minutes": {
            "task": "update_data_every_5_minutes",
            "schedule": crontab(minute="*/5"),
        },
        "run-every-5-seconds": {
            "task": "update_payment_status",
            "schedule": schedule(5.0),
        },
    }
