from aiohttp import web
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
from aiodataloader import DataLoader

from contests.config import CONFIG
from contests.schema import schema
from ..database import pgdb


class PostgresDataLoader(DataLoader):

    def __init__(self, pg_pool, loader):
        super().__init__()
        self.pg_pool = pg_pool
        self.loader = loader


    async def batch_load_fn(self, keys):
        return await self.loader(self.pg_pool, keys)


@web.middleware
async def dataloader_middleware(request, handler):
    pg_pool = request.app['pg_pool']
    request.app['data_loaders'] = {
        'user_by_api_key': PostgresDataLoader(pg_pool, pgdb.get_users_by_api_keys),
        'user_by_id': PostgresDataLoader(pg_pool, pgdb.get_users_by_ids),
        'names_by_contest_id': PostgresDataLoader(pg_pool, pgdb.get_names_by_contest_ids),
        'contests_by_created_by': PostgresDataLoader(pg_pool, pgdb.get_contests_by_created_bys)
    }
    return await handler(request)


async def startup(app):
    app['config'] = CONFIG

    app.router.add_route(
        '*',
        '/graphql',
        dataloader_middleware,
        GraphQLView(
            schema=schema,
            context={
                'pg_pool': app['pg_pool'],
                'mongo_db': app['mongo_db']
            },
            graphiql=True,
            executor=AsyncioExecutor(),
            enable_async=True)
        ,
        name='grqphql')


async def shutdown(app):
    pass
