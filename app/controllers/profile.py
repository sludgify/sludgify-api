from ..databases import UserDatabase
from flask import jsonify, send_from_directory
from ..utils import SendEmail
import re
from email_validator import validate_email
from ..serializers import UserSerializer


class ProfileController:
    def __init__(self):
        self.user_seliazer = UserSerializer()

    async def default_avatar(self):
        return send_from_directory(
            "static/images", "default-avatar.webp", mimetype="image/png"
        )

    async def update_email(self, user, email, otp, timestamp):
        errors = {}
        if email is None or (isinstance(email, str) and email.strip() == ""):
            errors.setdefault("email", []).append("IS_REQUIRED")
        else:
            if not isinstance(email, str):
                errors.setdefault("email", []).append("MUST_TEXT")
            try:
                valid = validate_email(email)
                email = valid.email
            except:
                errors.setdefault("email", []).append("IS_INVALID")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await UserDatabase.update(
                "email",
                user_id=user.id,
                created_at=int(timestamp.timestamp()),
                email=email,
                otp=otp,
            )
        ):
            return (
                jsonify(
                    {
                        "errors": {"otp": ["IS_INVALID"]},
                        "message": "invalid otp",
                    }
                ),
                400,
            )
        SendEmail.send_email(
            "Update Email",
            [email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Email</title>
</head>
<body>
    <p>Hello {user_data.username},</p>
    <p>your email has been updated to {user_data.email}</p>
</body>
</html>
                """,
        )
        user_me = self.user_seliazer.serialize(user_data.user)
        return (
            jsonify(
                {
                    "message": "success update email",
                    "data": user_me,
                }
            ),
            201,
        )

    async def update_password(self, user, password, confirm_password, timestamp):
        from ..extensions import bcrypt

        errors = {}
        if password is None or (isinstance(password, str) and password.strip() == ""):
            errors.setdefault("password", []).append("IS_REQUIRED")
        else:
            if not isinstance(password, str):
                errors.setdefault("password", []).append("MUST_TEXT")
        if confirm_password is None or (
            isinstance(confirm_password, str) and confirm_password.strip() == ""
        ):
            errors.setdefault("confirm_password", []).append("IS_REQUIRED")
        else:
            if not isinstance(confirm_password, str):
                errors.setdefault("confirm_password", []).append("MUST_TEXT")
        if password != confirm_password and (
            password or (isinstance(password, str) and not password.isspace())
        ):
            errors.setdefault("password_match", []).append("IS_MISMATCH")
        if isinstance(password, str) and password == confirm_password:
            if len(password) > 64:
                errors.setdefault("password_security", []).append("TOO_LONG")
            if len(password) < 8:
                errors.setdefault("password_security", []).append("TOO_SHORT")
            if not re.search(r"[A-Z]", password):
                errors.setdefault("password_security", []).append("NO_CAPITAL")
            if not re.search(r"[a-z]", password):
                errors.setdefault("password_security", []).append("NO_LOWERCASE")
            if not re.search(r"[0-9]", password):
                errors.setdefault("password_security", []).append("NO_NUMBER")
            if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
                errors.setdefault("password_security", []).append("NO_SYMBOL")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        result_password = bcrypt.generate_password_hash(password).decode("utf-8")
        if not (
            user_data := await UserDatabase.update(
                "password",
                user_id=user.id,
                created_at=int(timestamp.timestamp()),
                password=result_password,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update Password",
            [user.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Password</title>
</head>
<body>
    <p>Hello {user_data.username},</p>
    <p>your password has been updated</p>
</body>
</html>
                """,
        )
        user_me = self.user_seliazer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update password",
                    "data": user_me,
                }
            ),
            201,
        )

    async def update_last_name(self, user, last_name):
        errors = {}
        if last_name is None or (
            isinstance(last_name, str) and last_name.strip() == ""
        ):
            errors.setdefault("last_name", []).append("IS_REQUIRED")
        else:
            if not isinstance(last_name, str):
                errors.setdefault("last_name", []).append("MUST_TEXT")
            if isinstance(last_name, str) and len(last_name) < 5:
                errors.setdefault("last_name", []).append("TOO_SHORT")
            if isinstance(last_name, str) and len(last_name) > 15:
                errors.setdefault("last_name", []).append("TOO_LONG")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await UserDatabase.update(
                "last_name",
                user_id=user.id,
                last_name=last_name,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update Last Name",
            [user_data.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Last Name</title>
</head>
<body>
    <p>Hello {user_data.email},</p>
    <p>your Last Name has been updated to {last_name}</p>
</body>
</html>
                """,
        )
        user_me = self.user_seliazer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update last name",
                    "data": user_me,
                }
            ),
            201,
        )

    async def update_country(self, user, country):
        errors = {}
        if country is None or (isinstance(country, str) and country.strip() == ""):
            errors.setdefault("country", []).append("IS_REQUIRED")
        else:
            if not isinstance(country, str):
                errors.setdefault("country", []).append("MUST_TEXT")
            if isinstance(country, str) and len(country) < 5:
                errors.setdefault("country", []).append("TOO_SHORT")
            if isinstance(country, str) and len(country) > 15:
                errors.setdefault("country", []).append("TOO_LONG")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await UserDatabase.update(
                "country",
                user_id=user.id,
                country=country,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update Country",
            [user_data.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Country</title>
</head>
<body>
    <p>Hello {user_data.email},</p>
    <p>your Country has been updated to {country}</p>
</body>
</html>
                """,
        )
        user_me = self.user_seliazer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update country",
                    "data": user_me,
                }
            ),
            201,
        )

    async def update_first_name(self, user, first_name):
        errors = {}
        if first_name is None or (
            isinstance(first_name, str) and first_name.strip() == ""
        ):
            errors.setdefault("first_name", []).append("IS_REQUIRED")
        else:
            if not isinstance(first_name, str):
                errors.setdefault("first_name", []).append("MUST_TEXT")
            if isinstance(first_name, str) and len(first_name) < 5:
                errors.setdefault("first_name", []).append("TOO_SHORT")
            if isinstance(first_name, str) and len(first_name) > 15:
                errors.setdefault("first_name", []).append("TOO_LONG")
        if errors:
            return jsonify({"errors": errors, "message": "validation errors"}), 400
        if not (
            user_data := await UserDatabase.update(
                "first_name",
                user_id=user.id,
                first_name=first_name,
            )
        ):
            return (
                jsonify(
                    {
                        "message": "invalid or expired token",
                    }
                ),
                401,
            )
        SendEmail.send_email(
            "Update First Name",
            [user_data.email],
            f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update First Name</title>
</head>
<body>
    <p>Hello {user_data.email},</p>
    <p>your First Name has been updated to {first_name}</p>
</body>
</html>
                """,
        )
        user_me = self.user_seliazer.serialize(user_data)
        return (
            jsonify(
                {
                    "message": "successfully update first name",
                    "data": user_me,
                }
            ),
            201,
        )

    async def user_me(self, user):
        user_me = self.user_seliazer.serialize(user)
        return (
            jsonify(
                {
                    "message": "successfully get user",
                    "data": user_me,
                }
            ),
            200,
        )
