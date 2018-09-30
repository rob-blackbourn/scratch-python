from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLID,
    GraphQLString,
    GraphQLNonNull
)

from ...database import pgdb

NameType = GraphQLObjectType(
    name='Name',
    fields=lambda: {
        'id': GraphQLField(GraphQLID),
        'label': GraphQLField(GraphQLNonNull(GraphQLString)),
        'description': GraphQLField(GraphQLString),
        'createdAt': GraphQLField(GraphQLNonNull(GraphQLString)),
        'createdBy': GraphQLField(GraphQLNonNull(UserType), resolver=pgdb.get_user_by_id)
    }
)

# Located at end of file to avoid cyclic dependencies.
from .user import UserType
