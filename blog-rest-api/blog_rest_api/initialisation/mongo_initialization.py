import logging
logger = logging.getLogger(__name__)

from blog_rest_api.models import User, Permission, Post, Comment


async def setup_indexes(db):
    await User.q(db).create_indexes()
    await Permission.q(db).create_indexes()
    await Post.q(db).create_indexes()
    await Comment.q(db).create_indexes()


async def setup_admin_account(db, config):

    cursor = User.q(db).find({
        User.primary_email.s: config.authentication.admin_primary_email
    })

    if len(await cursor.to_list(1)) > 0:
        return

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


async def initialise_mongo(db, config):
    logging.debug('Initialising mongo ...')
    await setup_indexes(db)
    await setup_admin_account(db, config)
    logging.debug('... mongo initialised.')
