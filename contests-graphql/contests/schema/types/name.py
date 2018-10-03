from graphql import (
    GraphQLObjectType,
    GraphQLField,
    GraphQLID,
    GraphQLString,
    GraphQLNonNull
)

from ...utils.resolver import resolve_with_loader

NameType = GraphQLObjectType(
    name='Name',
    fields=lambda: {
        'id': GraphQLField(GraphQLID),
        'label': GraphQLField(GraphQLNonNull(GraphQLString)),
        'description': GraphQLField(GraphQLString),
        'createdAt': GraphQLField(GraphQLNonNull(GraphQLString)),
        'createdBy': GraphQLField(
            GraphQLNonNull(UserType),
            resolver=lambda name, info, **kwargs: resolve_with_loader(
                'user_by_id',
                info.context,
                name.createdBy,
                []
            )
        )
    }
)

# Located at end of file to avoid cyclic dependencies.
from .user import UserType
