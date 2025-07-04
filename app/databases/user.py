from .database import Database
from ..models import UserModel, OtpEmailModel


class UserDatabase(Database):
    @staticmethod
    async def insert(
        provider,
        avatar,
        first_name,
        last_name,
        company_name,
        email,
        password,
        created_at,
    ):
        user_data = UserModel(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            company_name=company_name,
            created_at=created_at,
            updated_at=created_at,
            provider=provider,
            avatar=avatar,
        )
        if provider == "google":
            user_data.is_active = True
        await user_data.unique_field()
        user_data.save()
        return user_data

    @staticmethod
    async def delete(category, **kwargs):
        pass

    @staticmethod
    async def update(category, **kwargs):
        user_id = kwargs.get("user_id")
        first_name = kwargs.get("first_name")
        last_name = kwargs.get("last_name")
        country = kwargs.get("country")
        password = kwargs.get("password")
        email = kwargs.get("email")
        created_at = kwargs.get("created_at")
        otp = kwargs.get("otp")
        if user_data := UserModel.objects(id=user_id).first():
            if category == "first_name":
                user_data.first_name = first_name
                user_data.save()
                return user_data
            if category == "country":
                user_data.country = country
                user_data.save()
                return user_data
            if category == "last_name":
                user_data.last_name = last_name
                user_data.save()
                return user_data
            if category == "password":
                user_data.password = password
                user_data.updated_at = created_at
                user_data.save()
                return user_data
            if category == "email":
                if data_otp := OtpEmailModel.objects(user=user_data, otp=otp).first():
                    user_data.email = email
                    user_data.updated_at = created_at
                    user_data.save()
                    data_otp.delete()
                    return data_otp

    @staticmethod
    async def get(category, **kwargs):
        email = kwargs.get("email")
        user_id = kwargs.get("user_id")
        if category == "by_email":
            if user_data := UserModel.objects(email=email.lower()).first():
                return user_data
        if category == "by_user_id":
            if user_data := UserModel.objects(id=user_id).first():
                return user_data
