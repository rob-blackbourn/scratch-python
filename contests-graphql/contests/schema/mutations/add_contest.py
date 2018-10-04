from graphql import (
    GraphQLInputObjectType,
    GraphQLInputObjectField,
    GraphQLField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLArgument
)

from ..types.contest_type import ContestType

from ...utils.resolver import resolver_wrapper
from ...database import pgdb

ContestInputType = GraphQLInputObjectType(
    name='ContestInput',
    fields=lambda: {
        'apiKey': GraphQLInputObjectField(GraphQLNonNull(GraphQLString)),
        'title': GraphQLInputObjectField(GraphQLNonNull(GraphQLString)),
        'description': GraphQLInputObjectField(GraphQLString)
    }
)
AddContestMutation = GraphQLField(
    ContestType,
    args={
        'input': GraphQLArgument(GraphQLNonNull(ContestInputType))
    },
    resolver=lambda _, info, **kwargs: resolver_wrapper(
        pgdb.add_new_contest,
        info.context['pg_pool'],
        kwargs.get('input', {})
    ))
