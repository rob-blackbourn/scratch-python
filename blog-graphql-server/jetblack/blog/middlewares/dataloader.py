from aiohttp import web
from ..data_loaders import user
from ..resolvers.db_dataloader import DbDataLoader


@web.middleware
async def dataloader_middleware(request, handler):
    db = request.app['mongo_db']
    request.app['data_loaders'] = {
        'user_by_id': DbDataLoader(db, user.get_users_by_ids),
        'user_by_primary_email': DbDataLoader(db, user.get_users_by_primary_emails),
        'roles_by_user_id': DbDataLoader(db, user.get_roles_by_user_ids)
    }
    return await handler(request)
