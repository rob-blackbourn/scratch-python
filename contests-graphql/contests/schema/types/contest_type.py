from collections import OrderedDict

from graphql import (
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
    GraphQLID,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLList
)

from ...database import pgdb

ContestStatusType = GraphQLEnumType(
    name='ContestStatusType',
    values=OrderedDict([
        ('draft', GraphQLEnumValue('draft')),
        ('published', GraphQLEnumValue('published')),
        ('archived', GraphQLEnumValue('archived')),
    ])
)

ContestType = GraphQLObjectType(
    name='ContestType',
    fields=lambda: {
        'id': GraphQLField(GraphQLID),
        'code': GraphQLField(GraphQLNonNull(GraphQLString)),
        'title': GraphQLField(GraphQLNonNull(GraphQLString)),
        'description': GraphQLField(GraphQLString),
        'status': GraphQLField(GraphQLNonNull(ContestStatusType)),
        'createdAt': GraphQLField(GraphQLNonNull(GraphQLString)),
        'names': GraphQLField(GraphQLList(NameType), resolver=pgdb.get_names)
    }
)

# Located at the end of the file to avoid cyclic dependencies
from .name import NameType
