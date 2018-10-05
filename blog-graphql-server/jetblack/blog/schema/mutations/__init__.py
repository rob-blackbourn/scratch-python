from graphql import (
    GraphQLObjectType,
)

RootMutationType = GraphQLObjectType(
    name='RootMutationType',
    fields=lambda: {
        'registerUser': RegisterUserMutation,
        'authenticateUser': AuthenticateUserMutation
    }
)

from .authentication_mutations import (RegisterUserMutation, AuthenticateUserMutation)
