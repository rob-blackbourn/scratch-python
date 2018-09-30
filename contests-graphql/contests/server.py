from aiohttp import web
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from contests.config import CONFIG
from contests.schema import schema
from contests.initialization import initialize

app = web.Application()
app['config'] = CONFIG

initialize(app)

web.run_app(app)
