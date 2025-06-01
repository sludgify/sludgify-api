import mongoengine as me


class TransactionPaymentModel(me.Document):
    description = me.StringField(required=True)
    unique_code = me.StringField(required=True, unique=True)
    created_at = me.IntField(required=True)
    expired_at = me.IntField(required=True)
    is_remove = me.BooleanField(required=False, default=False)

    user = me.ReferenceField("UserModel", reverse_delete_rule=me.CASCADE)

    meta = {"collection": "transaction_payments"}
