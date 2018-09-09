from datetime import datetime
from motorodm import (Document, StringField, ListField,
                      DateTimeField, ObjectIdField)

import bcrypt
from blog_graphql_api.config import CONFIG


def encrypt_password(password):
    salt = bcrypt.gensalt(CONFIG['authentication']['salt_rounds'])
    return bcrypt.hashpw(password.encode(), salt).decode()


class UserModel(Document):
    __collection__ = 'user'
    primary_email = StringField(required=True, unique=True)
    password = StringField(required=True, before_set=encrypt_password)
    secondary_emails = ListField(StringField(), required=False)
    given_names = ListField(StringField(allow_blank=False), required=False)
    family_name = StringField(required=False)
    nickname = StringField(required=False)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    def is_valid_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    async def before_create(self):
        self.created = self.updated = datetime.utcnow()

    async def before_update(self):
        self.updated = datetime.utcnow()
