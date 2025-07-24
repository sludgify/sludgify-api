import mongoengine as me


class CompanyInformationModel(me.Document):
    country = me.StringField(required=False)
    position = me.StringField(required=False)
    email = me.StringField(required=False)
    phone_number = me.StringField(required=False)
    address = me.StringField(required=False)
    company_name = me.StringField(required=False)

    user = me.ReferenceField("UserModel", reverse_delete_rule=me.CASCADE)

    meta = {"collection": "company_information"}

    async def unique_field(self):
        if self.email:
            self.email = self.email.lower()
        if self.position:
            self.position = self.position.lower()
        if self.country:
            self.country = self.country.lower()
        if self.phone_number:
            self.phone_number = self.phone_number.lower()
        if self.address:
            self.address = self.address.lower()
