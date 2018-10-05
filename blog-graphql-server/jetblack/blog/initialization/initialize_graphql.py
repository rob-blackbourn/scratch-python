from aiohttp import web
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from aiodataloader import DataLoader

from ..schema import schema
from ..resolvers import user_resolver


class DbDataLoader(DataLoader):

    def __init__(self, db, loader):
        super().__init__()
        self.db = db
        self.loader = loader


    async def batch_load_fn(self, keys):
        return await self.loader(self.db, keys)


@web.middleware
async def dataloader_middleware(request, handler):
    db = request.app['mongo_db']
    request.app['data_loaders'] = {
        'user_by_id': DbDataLoader(db, user_resolver.get_users_by_ids),
        'user_by_primary_email': DbDataLoader(db, user_resolver.get_users_by_primary_emails),
        'roles_by_user_id': DbDataLoader(db, user_resolver.get_roles_by_user_ids)
    }
    return await handler(request)


class CharPrintingMiddleware(object):
    def __init__(self, char):
        self.char = char


    async def resolve(self, next, root, info, *args, **kwargs):
        print(f'resolve() called for middleware {self.char}')
        # raise Exception('unauthenticated')
        result = await next(root, info, *args, **kwargs)
        print(f'then() for {self.char}')
        return result


async def startup(app):
    app.router.add_route(
        '*',
        '/graphql',
        dataloader_middleware,
        GraphQLView(
            schema=schema,
            context={
                'config': app['config'],
                'mongo_db': app['mongo_db']
            },
            graphiql=True,
            executor=AsyncioExecutor(),
            enable_async=True)
        ,
        name='grqphql')


async def shutdown(app):
    pass
