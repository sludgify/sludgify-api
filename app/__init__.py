from flask import Flask, request
import os
from .config import (
    database_mongodb,
    database_mongodb_url,
    smtp_host,
    smtp_port,
    smtp_email,
    smtp_password,
    celery_broker_url,
    celery_result_backend,
)
from .database import db
from .celery_app import celery_init_app
from .mail import mail
import datetime
from .models import (
    AccountActiveModel,
    ResetPasswordModel,
    OtpEmailModel,
    TransactionPaymentModel,
    WalletUserModel,
)
from celery.schedules import crontab, schedule
import asyncio


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    private_key_path = os.path.join(BASE_DIR, "keys", "private.pem")
    public_key_path = os.path.join(BASE_DIR, "keys", "public.pem")

    global PRIVATE_KEY, PUBLIC_KEY
    with open(private_key_path, "rb") as f:
        PRIVATE_KEY = f.read()

    with open(public_key_path, "rb") as f:
        PUBLIC_KEY = f.read()

    app.config.from_prefixed_env()
    app.config.from_mapping(
        CELERY=dict(
            broker_url=celery_broker_url,
            result_backend=celery_result_backend,
            task_ignore_result=True,
        ),
    )
    app.config["MONGODB_SETTINGS"] = {
        "db": database_mongodb,
        "host": database_mongodb_url,
        "connect": False,
    }
    app.config["MAIL_SERVER"] = smtp_host
    app.config["MAIL_PORT"] = smtp_port
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = smtp_email
    app.config["MAIL_PASSWORD"] = smtp_password
    app.config["MAIL_DEFAULT_SENDER"] = smtp_email

    global celery_app
    celery_app = celery_init_app(app)
    db.init_app(app)
    mail.init_app(app)

    def cancle_transaction(unique_code):
        from .utils import TransactionPayment

        transaction_payment = TransactionPayment()
        return asyncio.run(transaction_payment.cancel_transaction(unique_code))

    def check_transaction(unique_code):
        from .utils import TransactionPayment

        transaction_payment = TransactionPayment()
        return asyncio.run(transaction_payment.check_status(unique_code))

    @celery_app.task(name="update_data_every_5_minutes")
    def update_data_every_5_minutes():
        expired_at = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
        if data_account_active := AccountActiveModel.objects.all():
            for account_active_data in data_account_active:
                if account_active_data.expired_at <= expired_at:
                    account_active_data.delete()
                    print(f"success delete token {account_active_data.user.email}")
        if data_reset_password := ResetPasswordModel.objects.all():
            for reset_password_data in data_reset_password:
                if reset_password_data.expired_at <= expired_at:
                    reset_password_data.delete()
                    print(f"success delete token {reset_password_data.user.email}")
        if data_otp_email := OtpEmailModel.objects.all():
            for otp_email_data in data_otp_email:
                if otp_email_data.expired_at <= expired_at:
                    otp_email_data.delete()
                    print(f"success delete token {otp_email_data.user.email}")
        if data_transaction_payment := TransactionPaymentModel.objects.all():
            for transaction in data_transaction_payment:
                try:
                    if transaction.expired_at <= expired_at:
                        transaction.is_remove = True
                        transaction.save()
                        cancle_transaction(transaction.unique_code)
                        print(
                            f"success cancel transaction {transaction.user.username} | {transaction.unique_code}"
                        )
                except:
                    pass
        return "clear data"

    @celery_app.task(name="auto_payment")
    def auto_payment():
        if data_transaction_payment := TransactionPaymentModel.objects.all():
            for transaction in data_transaction_payment:
                try:
                    result = check_transaction(transaction.unique_code)
                    status = (
                        result.get("transaction_status")
                        if isinstance(result, dict)
                        else None
                    )
                    if status == "settlement":
                        if not transaction.is_remove:
                            transaction.is_remove = True
                            transaction.save()
                            if wallet_user := WalletUserModel.objects(
                                user=transaction.user
                            ).first():
                                wallet_user.wallet = (
                                    wallet_user.wallet + transaction.amount
                                )
                                wallet_user.save()
                                print(
                                    f"success update wallet {transaction.user.username} | {transaction.unique_code}"
                                )
                except Exception:
                    pass
        return "auto payment"

    celery_app.conf.beat_schedule = {
        "run-every-5-minutes": {
            "task": "update_data_every_5_minutes",
            "schedule": crontab(minute="*/5"),
        },
        "auto-payment": {
            "task": "auto_payment",
            "schedule": schedule(run_every=datetime.timedelta(seconds=15)),
        },
    }

    with app.app_context():
        from .api.register import register_router
        from .api.login import login_router
        from .api.account_active import account_active_router
        from .api.reset_password import reset_password_router
        from .api.me import me_router
        from .api.profile import profile_router
        from .api.otp_email import otp_email_router
        from .api.sludgify_analysis import sludgify_analysis_router
        from .api.carbon_credit import carbon_credit_router
        from .api.transaction_payment import transaction_payment_router

        app.register_blueprint(login_router)
        app.register_blueprint(register_router)
        app.register_blueprint(account_active_router)
        app.register_blueprint(reset_password_router)
        app.register_blueprint(me_router)
        app.register_blueprint(profile_router)
        app.register_blueprint(otp_email_router)
        app.register_blueprint(sludgify_analysis_router)
        app.register_blueprint(carbon_credit_router)
        app.register_blueprint(transaction_payment_router)

    @app.after_request
    async def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.before_request
    def before_request():
        request.timestamp = datetime.datetime.now(datetime.timezone.utc)

    return app
