from graphql import (
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLArgument,
    GraphQLList
)

from ..types.authentication_type import AuthenticationType

from ...utils.resolver import resolver_wrapper
from ...resolvers.user_resolver import (register_user, authenticate_user)

RegisterUserMutation = GraphQLField(
    AuthenticationType,
    args={
        'primaryEmail': GraphQLArgument(GraphQLNonNull(GraphQLString)),
        'password': GraphQLArgument(GraphQLNonNull(GraphQLString)),
        'secondaryEmails': GraphQLArgument(GraphQLString),
        'givenNames': GraphQLArgument(GraphQLList(GraphQLString)),
        'familyName': GraphQLArgument(GraphQLString),
        'nickname': GraphQLArgument(GraphQLString)
    },
    resolver=lambda _, info, **kwargs: resolver_wrapper(
        register_user,
        info.context['mongo_db'],
        info.context['config'],
        **kwargs
    ))

AuthenticateUserMutation = GraphQLField(
    AuthenticationType,
    args={
        'primaryEmail': GraphQLArgument(GraphQLNonNull(GraphQLString)),
        'password': GraphQLArgument(GraphQLNonNull(GraphQLString))
    },
    resolver=lambda _, info, *args, **kwargs: resolver_wrapper(
        authenticate_user,
        info.context['mongo_db'],
        info.context['config'],
        **kwargs
    ))
