from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
    GraphQLArgument
)

from ..utils.resolver import resolve_with_loader
from .types.user import UserType

RootQueryType = GraphQLObjectType(
    name='RootQueryType',
    fields=lambda: {
        'me': GraphQLField(
            UserType,
            args={
                'key': GraphQLArgument(GraphQLNonNull(GraphQLString))
            },
            description="The current user identified by an api key",
            resolver=lambda obj, info, **kwargs: resolve_with_loader(
                'user_by_api_key',
                info.context,
                kwargs['key']
            )
        )
    }
)

schema = GraphQLSchema(
    query=RootQueryType
)
