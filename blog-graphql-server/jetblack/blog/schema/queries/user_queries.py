from graphql import (
    GraphQLArgument,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
)

from ..types.user_type import UserType
from ...utils.resolver import resolve_with_loader

UserByIdQuery = GraphQLField(
    UserType,
    args={
        'id': GraphQLArgument(GraphQLNonNull(GraphQLString))
    },
    description="The user identified by their id",
    resolver=lambda obj, info, **kwargs: resolve_with_loader(
        'user_by_id',
        info.context,
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
        info.context,
        kwargs['email']
    )
)
