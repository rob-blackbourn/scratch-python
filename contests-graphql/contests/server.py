from aiohttp import web

from contests.config import CONFIG
from contests.initialization import initialize

app = web.Application()
app['config'] = CONFIG

initialize(app)

web.run_app(app)
