from ..models import CompanyInformationModel, CompanyNullModel
from .interfaces import SerializerInterface
from typing import Union


class CompanyInformationSerializer(SerializerInterface):
    def serialize(
        self,
        company_information: Union[CompanyInformationModel, CompanyNullModel],
        id_is_null: bool = False,
        country_is_null: bool = False,
        position_is_null: bool = False,
        email_is_null: bool = False,
        phone_number_is_null: bool = False,
        address_is_null: bool = False,
        company_name_is_null: bool = False,
    ) -> dict:
        data = {}
        if not id_is_null:
            data["id"] = str(company_information.id) if company_information.id else None
        if not country_is_null:
            data["country"] = company_information.country
        if not position_is_null:
            data["position"] = company_information.position
        if not email_is_null:
            data["email"] = company_information.email
        if not phone_number_is_null:
            data["phone_number"] = company_information.phone_number
        if not address_is_null:
            data["address"] = company_information.address
        if not company_name_is_null:
            data["company_name"] = company_information.user.company_name
        return data
