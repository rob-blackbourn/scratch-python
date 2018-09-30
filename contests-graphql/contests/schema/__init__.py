from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
    GraphQLArgument
)

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
            resolver=pgdb.get_user_by_api_key
        )
    }
)

schema = GraphQLSchema(
    query=RootQueryType
)
