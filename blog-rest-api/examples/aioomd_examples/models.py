# models.py

from datetime import datetime

from pymongo import IndexModel, DESCENDING
from bson import ObjectId

from aioodm import Document, EmbeddedDocument
from aioodm.fields import (
    StrField, BoolField, ListField, EmbDocField, RefField, SynonymField,
    IntField, FloatField, DateTimeField, ObjectIdField)

class User(Document):
    _id = StrField(regex=r'[a-zA-Z0-9_]{3, 20}')
    is_active = BoolField(default=True)
    posts = ListField(RefField('models.Post'), default=lambda: list())
    quote = StrField(required=False)

    # create a synonym field
    name = SynonymField(_id)

    class Meta:
        collection = 'users'

class Post(Document):
    # _id field will be added automatically as
    # _id = ObjectIdField(defalut=lambda: ObjectId())
    title = StrField(allow_blank=False, max_length=50)
    body = StrField()
    created = DateTimeField(default=lambda: datetime.utcnow())
    views = IntField(default=0)
    rate = FloatField(default=0.0)
    author = RefField(User, mongo_name='user')
    comments = ListField(EmbDocField('models.Comment'), default=lambda: list())

    class Meta:
        collection = 'posts'
        indexes = [IndexModel([('created', DESCENDING)])]
        default_sort = [('created', DESCENDING)]

class Comment(EmbeddedDocument):
    _id = ObjectIdField(default=lambda: ObjectId())
    author = RefField(User)
    body = StrField()

# `s` property of the fields can be used to get a mongodb string name
# to use in queries
assert User._id.s == '_id'
assert User.name.s == '_id'  # name is synonym
assert Post.title.s == 'title'
assert Post.author.s == 'user'  # field has mongo_name
assert Post.comments.body.s == 'comments.body'  # compound name