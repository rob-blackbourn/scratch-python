from motor.motor_asyncio import AsyncIOMotorClient


async def startup(app):
    config = app['config'].mongo
    client = AsyncIOMotorClient(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        authSource=config.auth_source
    )
    app['mongo_db'] = client[config.database]


async def shutdown(app):
    mongo_db = app['mongo_db']
    mongo_db.client.close()
