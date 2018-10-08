from datetime import (datetime, timedelta)
from easydict import EasyDict as edict
from graphql import GraphQLError
import jwt
from ..models import (User, Permission)
from ..utils.password import (encrypt_password, is_valid_password)
from ..utils.resolver import (organise, document_to_camelcase_dict)


def _signed_response(user, authentication):
    payload = {
        'iss': authentication.issuer,
        'sub': str(user.id),
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    token = jwt.encode(payload, key=authentication.secret).decode()
    return edict(token=token, message=f"Set the header 'Authorization' to 'Bearer {token}'")


async def get_users_by_ids(db, ids):
    cursor = User.qs(db).find(id={'$in': ids})
    users = await organise(cursor, ids, lambda user: user.id)
    return users


async def get_users_by_primary_emails(db, primary_emails):
    cursor = User.qs(db).find(primary_email={'$in': primary_emails})
    users = await organise(cursor, primary_emails, lambda user: user.primary_email)
    return users


async def register_user(context, primary_email, password, secondary_emails, given_names, family_name, nickname):
    hashed_password = encrypt_password(password, context.config.authentication.rounds)
    user = await User.qs(context.db).create(
        primary_email=primary_email,
        password=hashed_password,
        secondary_emails=secondary_emails,
        given_names=given_names,
        family_name=family_name,
        nickname=nickname
    )

    if await User.qs(context.db).count_documents() > 1:
        roles = context.config.authorization.default_roles
    else:
        roles = context.config.authorization.admin_roles

    await Permission.qs(context.db).create(user=user, roles=roles)
    return _signed_response(user, context.config.authentication)


async def authenticate_user(context, primary_email, password):
    user = await User.qs(context.db).find_one(primary_email=primary_email)
    if not is_valid_password(user.password, password):
        raise GraphQLError('unauthenticated')
    return _signed_response(user, context.config.authentication)


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


async def update_roles(authorize, context, primary_email, roles):
    if not authorize(context):
        raise GraphQLError('unauthorized')

    user = await User.qs(context.db).find_one(primary_email={'$eq': primary_email})
    permission = await Permission.qs(context.db).find_one(user={'$eq': user})
    permission.roles = roles
    await permission.qs(context.db).update()
    return document_to_camelcase_dict(user, edict())
