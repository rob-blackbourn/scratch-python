from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from contests.config import CONFIG
from contests.schema import schema


async def startup(app):
    app['config'] = CONFIG

    app.router.add_route(
        '*',
        '/graphql',
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
