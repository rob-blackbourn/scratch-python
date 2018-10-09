from easydict import EasyDict as edict
from graphql import (
    GraphQLArgument,
    GraphQLList,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
)

from ..types.user import UserType
from ...utils.resolver import resolve_with_loader, resolver_wrapper
from ...middlewares import authorize
from ...resolvers.user import get_all_users, get_current_user

UserByIdQuery = GraphQLField(
    UserType,
    args={
        'id': GraphQLArgument(GraphQLNonNull(GraphQLString))
    },
    description="The user identified by their id",
    resolver=lambda obj, info, **kwargs: resolve_with_loader(
        'user_by_id',
        authorize(any_role=['admin']),
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

UsersQuery = GraphQLField(
    GraphQLList(UserType),
    description='All of the the users',
    resolver=lambda obj, info, **kwargs: resolver_wrapper(
        get_all_users,
        authorize(any_role=['admin']),
        edict(info.context)
    )
)

CurrentUserQuery = GraphQLField(
    UserType,
    description='The current user',
    resolver=lambda obj, info, **kwargs: resolver_wrapper(
        get_current_user,
        edict(info.context)
    )
)
