from ..models import TransactionPaymentModel
from .interfaces import SerializerInterface


class TransactionPaymentSerializer(SerializerInterface):
    def serialize(
        self,
        transcation_data: TransactionPaymentModel,
        id_is_null: bool = False,
        description_is_null: bool = False,
        unique_code_is_null: bool = False,
        amount_is_null: bool = False,
        created_at_is_null: bool = False,
        expired_at_is_null: bool = False,
        payment_method_is_null: bool = False,
        payment_target_is_null: bool = False,
        status_is_null: bool = False,
        extra_fields: dict = None,
    ) -> dict:
        data = {}
        if not id_is_null:
            data["id"] = str(transcation_data.id) if transcation_data.id else None
        if not description_is_null:
            data["description"] = transcation_data.description
        if not unique_code_is_null:
            data["unique_code"] = transcation_data.unique_code
        if not amount_is_null:
            data["amount"] = transcation_data.amount
        if not created_at_is_null:
            data["created_at"] = transcation_data.created_at
        if not expired_at_is_null:
            data["expired_at"] = transcation_data.expired_at
        if not payment_method_is_null:
            data["payment_method"] = transcation_data.payment_method
        if not payment_target_is_null:
            data["payment_target"] = transcation_data.payment_target
        if not status_is_null:
            data["status"] = transcation_data.status
        if extra_fields:
            data.update(extra_fields)
        return data
