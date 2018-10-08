import os
from motor.motor_asyncio import AsyncIOMotorClient
import pytest

from jetblack.blog.models import (User, Permission)
from jetblack.blog.server import load_config
from jetblack.blog.resolvers.user import (register_user, authenticate_user)


@pytest.mark.asyncio
async def test_authenticate():
    config = load_config(os.path.join("..", "config", "blog-graphql-server-local.yml"))

    client = AsyncIOMotorClient(
        host=config.mongo.host,
        port=config.mongo.port,
        username=config.mongo.username,
        password=config.mongo.password,
        authSource=config.mongo.auth_source
    )

    db = client.testdb

    await db.drop_collection(User.__collection__)
    await db.drop_collection(Permission.__collection__)

    try:
        await User.qs(db).ensure_indices()

        user_args = {
            'primaryEmail': 'rob.blackbourn@gmail.com',
            'password': 'trustno1',
            'secondaryEmails': ['rob.blackbourn@yahoo.com'],
            'givenNames': ['Robert', 'Thomas'],
            'familyName': 'Blackbourn',
            'nickname': 'Rob'
        }
        register_response = await register_user(
            db,
            config,
            **user_args)
        assert 'token' in register_response

        login_response = await authenticate_user(
            db,
            config,
            **user_args)
        assert 'token' in login_response

        try:
            await authenticate_user(db, config.authentication.issuer, 'baduser@example.com')
            assert False
        except:
            assert True
    finally:
        await db.drop_collection(User.__collection__)
        await db.drop_collection(Permission.__collection__)
