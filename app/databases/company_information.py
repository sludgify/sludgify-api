from .database import Database
from ..models import UserModel, CompanyInformationModel


class CompanyInformationDatabase(Database):
    @staticmethod
    async def insert():
        pass

    @staticmethod
    async def get(category, **kwargs):
        user_id = kwargs.get("user_id")
        if category == "by_user_id":
            if user_data := UserModel.objects(id=user_id).first():
                if user_company_data := CompanyInformationModel.objects(
                    user=user_data
                ).first():
                    return user_company_data

    @staticmethod
    async def delete(category, **kwargs):
        pass

    @staticmethod
    async def update(category, **kwargs):
        user_id = kwargs.get("user_id")
        country = kwargs.get("country")
        position = kwargs.get("position")
        email = kwargs.get("email")
        phone_number = kwargs.get("phone_number")
        if user_data := UserModel.objects(id=user_id).first():
            if category == "country":
                if user_company_data := CompanyInformationModel.objects(
                    user=user_data
                ).first():
                    user_company_data.country = country
                    user_company_data.save()
                    return user_company_data
            if category == "position":
                if user_company_data := CompanyInformationModel.objects(
                    user=user_data
                ).first():
                    user_company_data.position = position
                    user_company_data.save()
                    return user_company_data
                else:
                    user_company_data = CompanyInformationModel(
                        position=position, user=user_data
                    )
                    user_company_data.save()
                    return user_company_data
            if category == "email":
                if user_company_data := CompanyInformationModel.objects(
                    user=user_data
                ).first():
                    user_company_data.email = email
                    user_company_data.save()
                else:
                    user_company_data = CompanyInformationModel(
                        email=email, user=user_data
                    )
                    user_company_data.save()
                return user_company_data
            if category == "phone_number":
                if user_company_data := CompanyInformationModel.objects(
                    user=user_data
                ).first():
                    user_company_data.phone_number = phone_number
                    user_company_data.save()
                    return user_company_data
