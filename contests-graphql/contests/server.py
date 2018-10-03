from aiohttp import web
from aiohttp_route_middleware import UrlDispatcherEx

from contests.config import CONFIG
from contests.initialization import initialize

app = web.Application(router=UrlDispatcherEx())

app['config'] = CONFIG

initialize(app)

web.run_app(app)
