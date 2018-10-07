from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from ..schema import schema
from ..middlewares import AuthenticationMiddleware, dataloader_middleware


async def startup(app):
    authentication = AuthenticationMiddleware(whitelist=[
        ['registerUser'],
        ['authenticate']
    ])

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
            middleware=[authentication],
            graphiql=True,
            executor=AsyncioExecutor(),
            enable_async=True)
        ,
        name='grqphql')


async def shutdown(app):
    pass
