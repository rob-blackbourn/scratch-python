from graphene import (Schema, ObjectType)
from .user_schema import UserQuery, UserMutation


class Query(UserQuery, ObjectType):
    pass


class Mutation(UserMutation, ObjectType):
    pass


schema = Schema(query=Query, mutation=Mutation)
