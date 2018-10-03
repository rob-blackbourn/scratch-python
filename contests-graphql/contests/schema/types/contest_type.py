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

from ...utils.resolver import resolve_with_loader

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
        'names': GraphQLField(
            GraphQLList(NameType),
            resolver=lambda contest, info, **kwargs: resolve_with_loader(
                'names_by_contest_id',
                info.context,
                contest.id,
                []
            ),
        ),
        'createdBy': GraphQLField(
            GraphQLNonNull(UserType),
            resolver=lambda name, info, **kwargs: resolve_with_loader(
                'user_by_id',
                info.context,
                name.createdBy
            )

        )
    }
)

# Located at the end of the file to avoid cyclic dependencies
from .name import NameType
from .user import UserType
