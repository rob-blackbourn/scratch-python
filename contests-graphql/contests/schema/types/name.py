from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLID,
    GraphQLString,
    GraphQLNonNull
)

from ...utils.resolver import resolver_wrapper
from ...database import pgdb

NameType = GraphQLObjectType(
    name='Name',
    fields=lambda: {
        'id': GraphQLField(GraphQLID),
        'label': GraphQLField(GraphQLNonNull(GraphQLString)),
        'description': GraphQLField(GraphQLString),
        'createdAt': GraphQLField(GraphQLNonNull(GraphQLString)),
        'createdBy': GraphQLField(
            GraphQLNonNull(UserType),
            resolver=lambda name, info, **kwargs: resolver_wrapper(
                pgdb.get_user_by_id,
                info.context['pg_pool'],
                name.createdBy
            )
        )
    }
)

# Located at end of file to avoid cyclic dependencies.
from .user import UserType
