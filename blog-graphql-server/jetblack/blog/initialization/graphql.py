import aiohttp_cors
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from ..schema import schema
from ..middlewares import AuthenticationMiddleware, dataloader_middleware


async def startup(app):
    authentication = AuthenticationMiddleware(whitelist=[
        ['registerUser'],
        ['authenticate']
    ])

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    route = app.router.add_route(
        'POST',
        '/graphql',
        dataloader_middleware,
        GraphQLView(
            schema=schema,
            context={
                'config': app['config'],
                'db': app['mongo_db']
            },
            middleware=[authentication],
            graphiql=True,
            executor=AsyncioExecutor(),
            enable_async=True)
        ,
        name='grqphql')

    cors.add(route)


async def shutdown(app):
    pass
