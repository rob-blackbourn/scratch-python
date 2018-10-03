from graphql import (
    GraphQLObjectType,
    GraphQLString,
    GraphQLInt,
    GraphQLField,
    GraphQLNonNull,
    GraphQLID,
    GraphQLList
)

from ...utils.resolver import resolver_wrapper, resolve_with_loader
from ...database import mdb

UserType = GraphQLObjectType(
    name='UserType',
    fields=lambda: {
        'id': GraphQLField(GraphQLID),
        'email': GraphQLField(GraphQLNonNull(GraphQLString)),
        'firstName': GraphQLField(GraphQLString),
        'lastName': GraphQLField(GraphQLString),
        'apiKey': GraphQLField(GraphQLNonNull(GraphQLString)),
        'createdAt': GraphQLField(GraphQLNonNull(GraphQLString)),
        'fullName': GraphQLField(GraphQLString, resolver=lambda obj, info: f"{obj.firstName} {obj.lastName}"),
        'contests': GraphQLField(
            GraphQLList(ContestType),
            resolver=lambda user, info, **kwargs: resolve_with_loader(
                'contests_by_created_by',
                info.context,
                user.id
            )
        ),
        'contestsCount': GraphQLField(
            GraphQLInt,
            resolver=lambda user, info, **kwargs: resolver_wrapper(
                mdb.get_counts,
                info.context['mongo_db'],
                user.id,
                info.field_name
            )
        ),
        'namesCount': GraphQLField(
            GraphQLInt,
            resolver=lambda user, info, **kwargs: resolver_wrapper(
                mdb.get_counts,
                info.context['mongo_db'],
                user.id,
                info.field_name
            )
        ),
        'votesCount': GraphQLField(
            GraphQLInt,
            resolver=lambda user, info, **kwargs: resolver_wrapper(
                mdb.get_counts,
                info.context['mongo_db'],
                user.id,
                info.field_name
            )
        ),
    }
)

# Located at end of file to avoid cyclic dependencies.
from .contest_type import ContestType
