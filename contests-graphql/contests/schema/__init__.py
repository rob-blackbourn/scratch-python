from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
    GraphQLArgument
)

from ..utils.resolver import resolver_wrapper
from ..database import pgdb
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
            resolver=lambda obj, info, **kwargs: resolver_wrapper(
                pgdb.get_user_by_api_key,
                info.context['pg_pool'],
                kwargs['key']
            )
        )
    }
)

schema = GraphQLSchema(
    query=RootQueryType
)
