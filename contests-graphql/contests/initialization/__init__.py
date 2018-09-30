from .initialize_postgres import (
    startup as startup_postgres,
    shutdown as shutdown_postgres
)
from .initialize_mongo import (
    startup as startup_mongo,
    shutdown as shutdown_mongo
)


def initialize(app):
    # Postgres
    app.on_startup.append(startup_postgres)
    app.on_shutdown.append(shutdown_postgres)

    # Mongo
    app.on_startup.append(startup_mongo)
    app.on_shutdown.append(shutdown_mongo)
