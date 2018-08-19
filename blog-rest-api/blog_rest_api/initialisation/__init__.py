from blog_rest_api.initialisation.mongo_initialization import initialise_mongo


async def initialse(app):
    await initialise_mongo(app['db'], app['config'])
