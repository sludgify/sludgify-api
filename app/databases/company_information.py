from .database import Database
from ..models import UserModel, CompanyInformationModel, CompanyNullModel


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
        address = kwargs.get("address")
        company_name = kwargs.get("company_name")
        if user_data := UserModel.objects(id=user_id).first():
            if category == "company_information":
                if user_company_data := CompanyInformationModel.objects(
                    user=user_data
                ).first():
                    if country:
                        user_company_data.country = country
                    if position:
                        user_company_data.position = position
                    if email:
                        user_company_data.email = email
                    if phone_number:
                        user_company_data.phone_number = phone_number
                    if address:
                        user_company_data.address = address
                    if company_name:
                        user_company_data.user.company_name = company_name
                    await user_company_data.user.unique_field()
                    await user_company_data.unique_field()
                    user_company_data.save()
                    resul_data = CompanyNullModel(
                        id=user_company_data.id,
                        country=user_company_data.country,
                        position=user_company_data.position,
                        email=user_company_data.email,
                        phone_number=user_company_data.phone_number,
                    )
                    return resul_data
                else:
                    user_company_data = CompanyInformationModel(
                        user=user_data,
                        country=country,
                        position=position,
                        email=email,
                        address=address,
                        phone_number=phone_number,
                    )
                    await user_company_data.unique_field()
                    user_company_data.save()
                    resul_data = CompanyNullModel(
                        id=user_company_data.id,
                        country=user_company_data.country,
                        position=user_company_data.position,
                        email=user_company_data.email,
                        phone_number=user_company_data.phone_number,
                    )
                    return resul_data
