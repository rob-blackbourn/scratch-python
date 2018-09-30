from graphql import (
    GraphQLObjectType,
    GraphQLString,
    GraphQLInt,
    GraphQLField,
    GraphQLNonNull,
    GraphQLID,
    GraphQLList
)

from ...database.pgdb import get_contests
from ...database.mdb import get_counts
from .contest_type import ContestType

MeType = GraphQLObjectType(
    name='Metype',
    fields=lambda: {
        'id': GraphQLField(GraphQLID),
        'email': GraphQLField(GraphQLNonNull(GraphQLString)),
        'firstName': GraphQLField(GraphQLString),
        'lastName': GraphQLField(GraphQLString),
        'apiKey': GraphQLField(GraphQLNonNull(GraphQLString)),
        'createdAt': GraphQLField(GraphQLNonNull(GraphQLString)),
        'fullName': GraphQLField(GraphQLString, resolver=lambda obj, info: f"{obj.firstName} {obj.lastName}"),
        'contests': GraphQLField(GraphQLList(ContestType), resolver=get_contests),
        'contestsCount': GraphQLField(GraphQLInt, resolver=get_counts),
        'namesCount': GraphQLField(GraphQLInt, resolver=get_counts),
        'votesCount': GraphQLField(GraphQLInt, resolver=get_counts),
    }
)
