from datetime import datetime

from pymongo import IndexModel, ASCENDING
from bson import ObjectId

from aioodm import ValidatingDocument
from aioodm.fields import (ObjectIdField, StrField,
                           ListField, RefField, DateTimeField)

from blog_rest_api.models.users import User


class Permission(ValidatingDocument):
    _id = ObjectIdField(required=True, default=lambda: ObjectId())
    user = RefField(User, required=True)
    roles = ListField(StrField(allow_blank=False, required=True))
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    class Meta:
        collection = 'permissions'
        indexes = [
            IndexModel([('user', ASCENDING)], unique=True)
        ]

    async def pre_save(self):
        timestamp = datetime.utcnow()
        if not self.created:
            self.created = timestamp
        self.updated = timestamp
