from datetime import datetime

from pymongo import IndexModel, ASCENDING
from bson import ObjectId

from aioodm import ValidatingDocument
from aioodm.fields import (StrField, ListField, DateTimeField, ObjectIdField)

import bcrypt
from blog_rest_api.config import CONFIG


def encrypt_password(password):
    salt = bcrypt.gensalt(CONFIG['authentication']['salt_rounds'])
    return bcrypt.hashpw(password.encode(), salt).decode()


class User(ValidatingDocument):
    _id = ObjectIdField(required=True, default=lambda: ObjectId())
    primary_email = StrField(allow_blank=False, required=True)
    password = StrField(allow_blank=False, required=True,
                        before_set=encrypt_password)
    secondary_emails = ListField(StrField(allow_blank=False), required=False)
    given_names = ListField(StrField(allow_blank=False), required=False)
    family_name = StrField(required=False)
    nickname = StrField(required=False, allow_blank=False)
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    class Meta:
        collection = 'users'
        indexes = [
            IndexModel([('primary_email', ASCENDING)], unique=True)
        ]

    def is_valid_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password.encode())

    async def pre_save(self):
        timestamp = datetime.utcnow()
        if not self.created:
            self.created = timestamp
        self.updated = timestamp
