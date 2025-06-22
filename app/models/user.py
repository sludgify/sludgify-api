import mongoengine as me


class UserModel(me.Document):
    first_name = me.StringField(required=False)
    last_name = me.StringField(required=False)
    company_name = me.StringField(required=False)
    email = me.StringField(required=True, unique=True)
    password = me.StringField(required=False)
    created_at = me.IntField(required=True)
    updated_at = me.IntField(required=True)
    provider = me.StringField(required=True)
    avatar = me.StringField(required=True)
    phone_number = me.StringField(required=False)
    is_active = me.BooleanField(required=False, default=False)

    meta = {"collection": "users"}

    async def unique_field(self):
        if self.first_name:
            self.first_name = self.first_name.lower()
        if self.email:
            self.email = self.email.lower()
        if self.last_name:
            self.last_name = self.last_name.lower()
        if self.company_name:
            self.company_name = self.company_name.lower()
