from graphql import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
    GraphQLArgument
)

from ..database import pgdb
from .types.me import MeType

RootQueryType = GraphQLObjectType(
    name='RootQueryType',
    fields=lambda: {
        'me': GraphQLField(
            MeType,
            args={
                'key': GraphQLArgument(GraphQLNonNull(GraphQLString))
            },
            description="The current user identified by an api key",
            resolver=pgdb.get_user
        )
    }
)

schema = GraphQLSchema(
    query=RootQueryType
)
