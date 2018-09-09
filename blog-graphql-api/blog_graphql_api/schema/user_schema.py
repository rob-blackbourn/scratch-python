from datetime import datetime, timedelta
from graphene import (Mutation, ObjectType, Field, String, List, NonNull, ID)
import jwt
from motorodm.graphene import MotorOdmObjectType
from ..models import UserModel, PermissionModel
from ..config import CONFIG


def has_any_role(required_roles, user_roles):
    if not required_roles or len(required_roles) == 0:
        return True

    for required_role in required_roles:
        if required_role in user_roles:
            return True

    return False


def has_all_roles(required_roles, user_roles):
    if not required_roles or len(required_roles) == 0:
        return True

    for required_role in required_roles:
        if required_role not in user_roles:
            return False

    return True


def sign(id):
    payload = {
        'iss': CONFIG['authentication']['issuer'],
        'sub': str(id),
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, key=CONFIG['authentication']['secret']).decode()


class UserSchema(MotorOdmObjectType):

    class Meta:
        model = UserModel


class RegisterUser(Mutation):

    Output = String

    class Arguments:
        primary_email = String(required=True)
        password = String(required=True)
        secondary_emails = List(String())
        given_names = List(String())
        family_name = String()
        nickname = String()

    async def mutate(self, info, **kwargs):
        db = info.context['db']
        user = await UserModel.qs(db).create(**kwargs)
        await PermissionModel.qs(db).create(
            user=user,
            roles=CONFIG['authorization']['default_roles'])

        token = sign(user._id)
        return token


class LoginUser(Mutation):

    Output = String()

    class Arguments:
        email = String(required=True)
        password = String(required=True)

    async def mutate(self, info, email, password):
        user = await UserModel.qs(info.context['db']).find_one(primary_email=email)
        if not user.is_valid_password(password):
            raise Exception('invalid password')
        token = sign(user._id)
        return token


class UserQuery:
    users = List(UserModel)
    user = Field(UserModel, id=ID(), primary_email=String())

    async def resolve_users(self, info, **kwargs):
        cursor = UserModel.qs(info.context['db']).find(**kwargs)
        return [user async for user in cursor]

    async def resolve_user(self, info, **kwargs):
        return await UserModel.qs(info.context['db']).find_one(**kwargs)


class UserMutation:

    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()
