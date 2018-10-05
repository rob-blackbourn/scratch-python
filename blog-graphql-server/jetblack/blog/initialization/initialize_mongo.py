from motor.motor_asyncio import AsyncIOMotorClient

from ..models import (User, Permission)


async def startup(app):
    config = app['config'].mongo

    client = AsyncIOMotorClient(
        host=config.host,
        port=config.port,
        username=config.username,
        password=config.password,
        authSource=config.auth_source
    )

    db = client[config.database]

    await User.qs(db).ensure_indices()
    await Permission.qs(db).ensure_indices()

    app['mongo_db'] = db


async def shutdown(app):
    mongo_db = app['mongo_db']
    mongo_db.client.close()
