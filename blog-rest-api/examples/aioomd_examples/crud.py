import asyncio
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from examples.aioomd_examples.models import User


async def go(db):
    # create model's indexes
    await User.q(db).create_indexes()

    # CREATE
    # create using save
    # Note: if do_insert=False (default) save performs a replace
    # with upsert=True, so it does not raise if _id already exists
    # in db but replace document with that _id.
    u = await User(name='Alexandro').save(db, do_insert=True)
    assert u.name == 'Alexandro'
    assert u._id == 'Alexandro'
    assert u.is_active is True
    assert u.posts == []
    assert u.quote is None
    # create using create
    u = await User.create(db, name='Francesco')
    # using query
    u = await User.q(db).create(name='Ihor', is_active=False)

    # READ
    # get by id
    u = await User.q(db).get('Alexandro')
    assert u.name == 'Alexandro'
    # find
    users = await User.q(db).find({User.is_active.s: True}).to_list(10)
    assert len(users) == 2
    # using for loop
    users = []
    async for user in User.q(db).find({User.is_active.s: False}):
        users.append(user)
    assert len(users) == 1
    # in Python 3.6 an up use async comprehensions
    users = [user async for user in User.q(db).find({})]
    assert len(users) == 3

    # UPDATE
    u = await User.q(db).get('Ihor')
    u.is_active = True
    await u.save(db)
    assert (await User.q(db).get('Ihor')).is_active is True
    # using update (without data validation)
    # object is reloaded from db after update.
    await u.update(db, {'$push': {User.posts.s: ObjectId()}})

    # DELETE
    u = await User.q(db).get('Ihor')
    await u.delete(db)


loop = asyncio.get_event_loop()
client = AsyncIOMotorClient(io_loop=loop)
db = client.test_aioodm
loop.run_until_complete(go(db))
