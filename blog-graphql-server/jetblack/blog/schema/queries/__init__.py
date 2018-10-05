from graphql import (
    GraphQLObjectType,
)

RootQueryType = GraphQLObjectType(
    name='RootQueryType',
    fields=lambda: {
        'userById': UserByIdQuery,
        'userByPrimaryEmail': UserByPrimaryEmailQuery
    }
)

from .user_queries import (UserByIdQuery, UserByPrimaryEmailQuery)
