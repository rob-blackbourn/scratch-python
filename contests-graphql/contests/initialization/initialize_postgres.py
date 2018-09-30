import asyncpg


async def startup(app):
    config = app['config'].postgres
    app['pg_pool'] = await asyncpg.create_pool(
        database=config.database,
        user=config.user,
        password=config.password,
        host=config.host)


async def shutdown(app):
    await app['pg_pool'].close()
