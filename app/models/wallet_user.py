import mongoengine as me


class WalletUserModel(me.Document):
    created_at = me.IntField(required=True)
    updated_at = me.IntField(required=True)
    wallet = me.IntField(required=False, default=0)

    user = me.ReferenceField("UserModel", reverse_delete_rule=me.CASCADE)

    meta = {"collection": "wallet_users"}
