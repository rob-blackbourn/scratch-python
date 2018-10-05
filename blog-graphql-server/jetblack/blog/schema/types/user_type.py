from graphql import (
    GraphQLObjectType,
    GraphQLString,
    GraphQLField,
    GraphQLNonNull,
    GraphQLID,
    GraphQLList,
    GraphQLArgument
)

from ...utils.resolver import resolve_with_loader

UserType = GraphQLObjectType(
    name='UserType',
    fields=lambda: {
        'id': GraphQLField(GraphQLID),
        'primaryEmail': GraphQLField(GraphQLNonNull(GraphQLString)),
        'password': GraphQLField(GraphQLNonNull(GraphQLString)),
        'secondaryEmails': GraphQLField(GraphQLString),
        'givenNames': GraphQLField(GraphQLList(GraphQLString)),
        'familyName': GraphQLField(GraphQLString),
        'nickname': GraphQLField(GraphQLString),
        'created': GraphQLField(GraphQLNonNull(GraphQLString)),
        'updated': GraphQLField(GraphQLNonNull(GraphQLString)),
        'roles': GraphQLField(
            GraphQLList(GraphQLString),
            resolver=lambda user, info, **kwargs: resolve_with_loader(
                'roles_by_user_id',
                info.context,
                user.id
            )
        )
    }
)
