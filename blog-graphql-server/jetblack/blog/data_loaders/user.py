from ..models import User, Permission
from ..utils.resolver import organise


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


async def get_users_by_ids(db, ids):
    cursor = User.qs(db).find(id={'$in': ids})
    users = await organise(cursor, ids, lambda user: user.id)
    return users


async def get_users_by_primary_emails(db, primary_emails):
    cursor = User.qs(db).find(primary_email={'$in': primary_emails})
    users = await organise(cursor, primary_emails, lambda user: user.primary_email)
    return users
