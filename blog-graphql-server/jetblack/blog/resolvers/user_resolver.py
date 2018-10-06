from datetime import (datetime, timedelta)
from easydict import EasyDict as edict
from graphql import GraphQLError
import jwt
from stringcase import (snakecase)
from ..models import (User, Permission)
from ..utils.password import (encrypt_password, is_valid_password)
from ..utils.resolver import organise


def sign(sub, issuer, secret):
    payload = {
        'iss': issuer,
        'sub': sub,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, key=secret).decode()


def signed_response(user, issuer, secret):
    token = sign(str(user.id), issuer, secret)
    return edict(token=token, message=f"Set the header 'Authorization' to 'Bearer {token}'")


async def get_default_roles(db, config):
    if await User.qs(db).count_documents() > 1:
        return config.authorization.default_roles
    return ['admin'] + config.authorization.default_roles + config.authorization.approved_roles


async def get_users_by_ids(db, ids):
    cursor = User.qs(db).find(id={'$in': ids})
    users = await organise(cursor, ids, lambda user: user.id)
    return users


async def get_users_by_primary_emails(db, primary_emails):
    cursor = User.qs(db).find(primary_email={'$in': primary_emails})
    users = await organise(cursor, primary_emails, lambda user: user.primary_email)
    return users


async def register_user(db, config, **kwargs):
    user_args = {snakecase(k): v for k, v in kwargs.items()}
    user_args['password'] = encrypt_password(user_args['password'], config.authentication.rounds)
    user = await User.qs(db).create(**user_args)
    roles = await get_default_roles(db, config)
    await Permission.qs(db).create(user=user, roles=roles)
    return signed_response(user, config.authentication.issuer, config.authentication.secret)


async def authenticate_user(db, config, **kwargs):
    user_args = {snakecase(k): v for k, v in kwargs.items()}
    user = await User.qs(db).find_one(primary_email=user_args['primary_email'])
    if not is_valid_password(user.password, user_args['password']):
        raise GraphQLError('unauthenticated')
    return signed_response(user, config.authentication.issuer, config.authentication.secret)


async def get_roles_by_user_ids(db, user_ids):
    users = [User(id=id) for id in user_ids]
    cursor = Permission.qs(db).find(user={'$in': users})
    permissions = await organise(
        cursor,
        user_ids,
        lambda permission: permission.user._identity,
        lambda permission: permission.roles,
        True)
    return permissions
