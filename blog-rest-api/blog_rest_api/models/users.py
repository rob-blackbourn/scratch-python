from datetime import datetime

from pymongo import IndexModel, ASCENDING

from aioodm import ValidatingDocument
from aioodm.fields import (StrField, ListField, DateTimeField)

import bcrypt
from blog_rest_api.config import CONFIG


def encrypt_password(password):
    salt = bcrypt.gensalt(CONFIG['authentication']['salt_rounds'])
    return bcrypt.hashpw(password.encode(), salt).decode()


class User(ValidatingDocument):
    primary_email = StrField(allow_blank=False, required=True)
    password = StrField(allow_blank=False, required=True,
                        before_set=encrypt_password)
    secondary_emails = ListField(StrField(allow_blank=False))
    given_names = ListField(StrField(allow_blank=False))
    family_name = StrField()
    nickname = StrField(required=True, allow_blank=False)
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
