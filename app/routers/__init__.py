from .register import register_router
from .login import login_router
from .account_active import account_active_router
from .reset_password import reset_password_router
from .me import me_router
from .profile import profile_router
from .otp_email import otp_email_router
from .carbon_credit import carbon_credit_router
from .sludgify_analysis import sludgify_analysis_router
from .transaction_payment import transaction_payment_router
from .company_information import company_information_router
from .calculator import calculator_router


def register_blueprints(app):
    app.register_blueprint(register_router)
    app.register_blueprint(login_router)
    app.register_blueprint(account_active_router)
    app.register_blueprint(reset_password_router)
    app.register_blueprint(me_router)
    app.register_blueprint(profile_router)
    app.register_blueprint(otp_email_router)
    app.register_blueprint(carbon_credit_router)
    app.register_blueprint(sludgify_analysis_router)
    app.register_blueprint(transaction_payment_router)
    app.register_blueprint(company_information_router)
    app.register_blueprint(calculator_router)
