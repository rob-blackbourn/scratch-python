from datetime import datetime

from pymongo import IndexModel, ASCENDING
from bson import ObjectId

from aioodm import ValidatingDocument
from aioodm.fields import (
    StrField, ListField, DateTimeField, ObjectIdField, RefField)

from blog_rest_api.models.users import User
from blog_rest_api.models.posts import Post


class Comment(ValidatingDocument):
    _id = ObjectIdField(required=True, default=lambda: ObjectId())
    user = RefField(User, required=True)
    post = RefField(User, required=True)
    in_response_to = ObjectIdField()
    content = StrField(allow_blank=False, required=True)

    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    class Meta:
        collection = 'comments'

    async def pre_save(self):
        timestamp = datetime.utcnow()
        if not self.created:
            self.created = timestamp
        self.updated = timestamp
