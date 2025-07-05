import mongoengine as me


class ChatHistoryModel(me.Document):
    room = me.StringField(required=True)
    original_message = me.StringField(required=True)
    response_message = me.StringField(required=True)
    links = me.ListField(me.StringField())
    created_at = me.IntField(required=True)

    user = me.ReferenceField("UserModel", reverse_delete_rule=me.CASCADE)

    meta = {"collection": "chat_history"}
