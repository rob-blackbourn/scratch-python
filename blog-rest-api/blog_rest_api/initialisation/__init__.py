from blog_rest_api.initialisation.mongo_initialization import initialize_mongo
from blog_rest_api.initialisation.controller_configuration import configure_controllers


async def initialize(app):
    await initialize_mongo(app['db'], app['config'])


def configure(app, db, config):
    configure_controllers(app, db, config)
