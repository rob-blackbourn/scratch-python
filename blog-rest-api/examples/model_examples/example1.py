import asyncio
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from blog_rest_api.models.users import User
from blog_rest_api.models.permissions import Permission


async def go(db):
    # create model's indexes
    await User.q(db).create_indexes()

    user = await User.create(
        db,
        primary_email='rob.blackbourn@googlemail.com',
        secondary_emails=['rob.blackbourn@gmail.com'],
        password='foo',
        given_names=['Robert', 'Thomas'],
        family_name='Blackbourn',
        nickname='Rob'
    )

    assert user.is_valid_password('foo')

    user.password = 'bar'
    await user.save(db)

    assert not user.is_valid_password('foo')
    assert user.is_valid_password('bar')

    permission = await Permission.create(
        db,
        user=user,
        roles=['post:read', 'post:write']
    )

    await permission.delete(db)

    await user.delete(db)

    # using query
    u = await User.q(db).create(
        primary_email='rob.blackbourn@googlemail.com',
        secondary_emails=['rob.blackbourn@gmail.com'],
        password='trustno1',
        given_names=['Robert', 'Thomas'],
        family_name='Blackbourn',
        nickname='Rob'
    )

    # READ
    # get by id
    u = await User.q(db).get(u._id)

    # find
    users = await User.q(db).find({User.nickname.s: 'Rob'}).to_list(10)
    assert len(users) == 1

    # using for loop
    users = []
    async for user in User.q(db).find({User.nickname.s: 'Rob'}):
        users.append(user)

    assert len(users) == 1

    # in Python 3.6 an up use async comprehensions
    users = [user async for user in User.q(db).find({})]
    assert len(users) == 1

    # UPDATE
    u = users[0]
    u.nickname = 'Rob Tom'
    await u.save(db)
    # assert (await User.q(db).get('Ihor')).is_active is True
    # using update (without data validation)
    # object is reloaded from db after update.
    # await u.update(db, {'$push': {User.posts.s: ObjectId()}})

    # DELETE
    await u.delete(db)


loop = asyncio.get_event_loop()
client = AsyncIOMotorClient(io_loop=loop)
db = client.test_models
loop.run_until_complete(go(db))
