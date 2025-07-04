from ..models import company_information
from .interfaces import SerializerInterface


class CompanyInformationSerializer(SerializerInterface):
    def serialize(
        self,
        company_information: company_information,
        id_is_null: bool = False,
        country_is_null: bool = False,
        position_is_null: bool = False,
        email_is_null: bool = False,
        phone_number_is_null: bool = False,
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
        return data
