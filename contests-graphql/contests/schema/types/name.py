from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLID,
    GraphQLString,
    GraphQLNonNull
)

from ...database import pgdb


def fields():
    from .user import UserType
    return {
        'id': GraphQLField(GraphQLID),
        'label': GraphQLField(GraphQLNonNull(GraphQLString)),
        'description': GraphQLField(GraphQLString),
        'createdAt': GraphQLField(GraphQLNonNull(GraphQLString)),
        'createdBy': GraphQLField(GraphQLNonNull(UserType), resolver=pgdb.get_user_by_id)
    }


NameType = GraphQLObjectType(
    name='Name',
    fields=fields
)
