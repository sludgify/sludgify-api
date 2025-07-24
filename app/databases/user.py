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
        position = kwargs.get("position")
        password = kwargs.get("password")
        email = kwargs.get("email")
        created_at = kwargs.get("created_at")
        phone_number = kwargs.get("phone_number")
        deleted_id = kwargs.get("deleted_id")
        avatar = kwargs.get("avatar")
        if user_data := UserModel.objects(id=user_id).first():
            if category == "password":
                user_data.password = password
                user_data.updated_at = created_at
                user_data.save()
                return user_data
            if category == "profile":
                if first_name:
                    user_data.first_name = first_name
                if last_name:
                    user_data.last_name = last_name
                if country:
                    user_data.country = country
                if position:
                    user_data.position = position
                if email:
                    user_data.email = email
                if avatar:
                    user_data.avatar = avatar
                if phone_number:
                    user_data.phone_number = phone_number
                await user_data.unique_field()
                user_data.save()
                return user_data
            if category == "deleted_id_by_user_id":
                user_data.deleted_id = deleted_id
                user_data.updated_at = created_at
                user_data.save()
                return user_data
            if category == "cancle_deleted_id_by_user_id":
                user_data.deleted_id = None
                user_data.save()
                return user_data

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
