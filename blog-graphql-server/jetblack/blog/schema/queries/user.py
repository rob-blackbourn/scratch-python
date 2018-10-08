from easydict import EasyDict as edict
from graphql import (
    GraphQLArgument,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
)

from ..types.user import UserType
from ...utils.resolver import resolve_with_loader
from ...middlewares import authorize

UserByIdQuery = GraphQLField(
    UserType,
    args={
        'id': GraphQLArgument(GraphQLNonNull(GraphQLString))
    },
    description="The user identified by their id",
    resolver=lambda obj, info, **kwargs: resolve_with_loader(
        'user_by_id',
        edict(info.context),
        kwargs['id']
    )
)

UserByPrimaryEmailQuery = GraphQLField(
    UserType,
    args={
        'email': GraphQLArgument(GraphQLNonNull(GraphQLString))
    },
    description="The user identified by their primary email address",
    resolver=lambda obj, info, **kwargs: resolve_with_loader(
        'user_by_primary_email',
        authorize(any_role=['admin']),
        edict(info.context),
        kwargs['email']
    )
)
