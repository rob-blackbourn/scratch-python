import pytest
import asyncpg
from contests.database import pgdb
from contests.initialization.initialise_graphql import PostgresDataLoader
from contests.utils.asyncpg import row_to_camelcase_edict, rows_to_camelcase_edict


async def get_user_by_api_key(pg_pool, api_key):
    async with pg_pool.acquire() as connection:
        row = await connection.fetchrow('select * from users where api_key = $1', api_key)
    if not row:
        raise ValueError('Not found')
    return row_to_camelcase_edict(row)


async def get_user_by_id(pg_pool, id):
    async with pg_pool.acquire() as connection:
        row = await connection.fetchrow('select * from users where id = $1', id)
    if not row:
        raise ValueError('Not found')
    return row_to_camelcase_edict(row)


async def get_contests_by_created_by(pg_pool, created_by):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from contests where created_by = $1', created_by)
    return rows_to_camelcase_edict(rows)


async def get_names_by_contest_id(pg_pool, contest_id):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from names where contest_id = $1', contest_id)
    return rows_to_camelcase_edict(rows)


@pytest.mark.asyncio
async def test_postgres_dataloader():
    pool = await asyncpg.create_pool(
        database='contests',
        user='rtb',
        password='trustno1',
        host='localhost')

    user_by_api_key_dataloader = PostgresDataLoader(pool, pgdb.get_users_by_api_keys)
    contests_by_created_by = PostgresDataLoader(pool, pgdb.get_contests_by_created_bys)
    names_by_contest_ids = PostgresDataLoader(pool, pgdb.get_names_by_contest_ids)
    user_by_id_dataloaded = PostgresDataLoader(pool, pgdb.get_users_by_ids)

    samer0 = await get_user_by_api_key(pool, '4242')
    samer1 = await user_by_api_key_dataloader.load('4242')
    assert samer0 == samer1

    creative0 = await get_user_by_api_key(pool, '0000')
    creative1 = await user_by_api_key_dataloader.load('0000')
    assert creative1 == creative0

    contests0 = await get_contests_by_created_by(pool, samer0.id)
    contests1 = await contests_by_created_by.load(samer1.id)
    assert contests0 == contests1

    for contest in contests0:
        names0 = await get_names_by_contest_id(pool, contest.id)
        names1 = (await names_by_contest_ids.load(contest.id)) or []
        assert names1 == names0
        for name in names0:
            created_by0 = await get_user_by_id(pool, name.createdBy)
            created_by1 = await user_by_id_dataloaded.load(name.createdBy)
            assert created_by1 == created_by0
