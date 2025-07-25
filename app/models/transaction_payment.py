import mongoengine as me


class TransactionPaymentModel(me.Document):
    description = me.StringField(required=True)
    unique_code = me.StringField(required=True, unique=True)
    amount = me.IntField(required=True)
    created_at = me.IntField(required=True)
    expired_at = me.IntField(required=True)
    payment_method = me.StringField(required=True)
    payment_target = me.StringField(required=True)
    status = me.StringField(required=False, default="pending")

    user = me.ReferenceField("UserModel", reverse_delete_rule=me.CASCADE)

    meta = {"collection": "transaction_payments"}
