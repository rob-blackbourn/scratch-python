import logging
logger = logging.getLogger(__name__)

from aiohttp import web
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from blog_rest_api.config import CONFIG
from blog_rest_api.controllers import AuthController, UserController
from blog_rest_api.models import (User, Permission)
from blog_rest_api.utils import Struct


async def initialise_mongo(db, config):
    logging.debug('Initialising mongo ...')
    await User.q(db).create_indexes()
    await Permission.q(db).create_indexes()

    if 0 == len(await User.q(db).find({User.primary_email.s: config.authentication.admin_primary_email}).to_list(1)):
        logging.debug('Creating the admin user')
        admin = await User.create(
            db,
            primary_email=config.authentication.admin_primary_email,
            password=config.authentication.admin_default_password,
            nickname='Administrator',
        )
        await Permission.create(
            db,
            user=admin,
            roles=['admin']
        )
    logging.debug('... mongo initialised.')


async def initialse(app):
    await initialise_mongo(app['db'], app['config'])


def start():

    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    client = AsyncIOMotorClient(io_loop=loop)

    app = web.Application()

    app['db'] = client.blog
    app['config'] = Struct(CONFIG)

    app.on_startup.append(initialse)

    auth_controller = AuthController(app['db'], app['config'])
    admin = auth_controller.create_app()
    app.add_subapp('/admin/', admin)

    user_controller = UserController(app['db'], app['config'])
    user_app = user_controller.create_app(
        auth_controller.authenticate,
        auth_controller.authorise(['admin']),
        auth_controller.authorise(['admin']))
    app.add_subapp('/user/', user_app)

    web.run_app(app)


if __name__ == "__main__":
    start()
