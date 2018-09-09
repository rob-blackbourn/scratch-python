from datetime import datetime

from motorodm import (
    Document,
    ObjectIdField,
    StringField,
    ListField,
    ReferenceField,
    DateTimeField
)

from blog_graphql_api.models.user_model import UserModel


class PermissionModel(Document):
    __collection__ = 'permission'
    user = ReferenceField(UserModel, required=True, unique=True)
    roles = ListField(StringField(required=True))
    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)

    async def before_create(self):
        self.created = self.updated = datetime.utcnow()

    async def before_update(self):
        self.updated = datetime.utcnow()
