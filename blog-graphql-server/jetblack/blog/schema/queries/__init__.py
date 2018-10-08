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

from .user import (UserByIdQuery, UserByPrimaryEmailQuery)
