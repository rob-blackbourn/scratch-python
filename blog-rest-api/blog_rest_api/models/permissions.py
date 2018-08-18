from datetime import datetime

from pymongo import IndexModel, DESCENDING

from aioodm import ValidatingDocument
from aioodm.fields import (
    StrField, BoolField, ListField, EmbDocField, RefField, SynonymField,
    IntField, FloatField, DateTimeField, ObjectIdField)

from blog_rest_api.models.users import User


class Permission(ValidatingDocument):
    user = RefField(User, required=True)
    roles = ListField(StrField(allow_blank=False, required=True))
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    class Meta:
        collection = 'permissions'

    async def pre_save(self):
        timestamp = datetime.utcnow()
        if not self.created:
            self.created = timestamp
        self.updated = timestamp
