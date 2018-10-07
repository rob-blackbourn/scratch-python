from easydict import EasyDict as edict
from graphql import (
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLArgument,
    GraphQLList
)

from ..types import (
    AuthenticationType,
    UserType
)

from ...utils.resolver import resolver_wrapper
from ...resolvers.user_resolver import (
    register_user,
    authenticate_user,
    update_roles
)
from ...middlewares import authorize

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
        kwargs['primaryEmail'],
        kwargs['password'],
        kwargs.get('secondaryEmails', None),
        kwargs.get('givenNames', None),
        kwargs.get('familyName', None),
        kwargs.get('nickname', None)
    ))

AuthenticateMutation = GraphQLField(
    AuthenticationType,
    args={
        'primaryEmail': GraphQLArgument(GraphQLNonNull(GraphQLString)),
        'password': GraphQLArgument(GraphQLNonNull(GraphQLString))
    },
    resolver=lambda _, info, *args, **kwargs: resolver_wrapper(
        authenticate_user,
        info.context['mongo_db'],
        info.context['config'],
        kwargs['primaryEmail'],
        kwargs['password']
    ))

UpdateRolesMutation = GraphQLField(
    UserType,
    args={
        'primaryEmail': GraphQLArgument(GraphQLNonNull(GraphQLString)),
        'roles': GraphQLArgument(GraphQLList(GraphQLString))
    },
    resolver=lambda _, info, *args, **kwargs: resolver_wrapper(
        update_roles,
        authorize(any_role=['admin']),
        edict(info.context),
        kwargs['primaryEmail'],
        kwargs['roles']
    )
)
