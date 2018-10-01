from easydict import EasyDict as edict
from stringcase import camelcase


def row_to_camelcase_edict(row):
    return edict({camelcase(k): v for k, v in row.items()})


def rows_to_camelcase_edict(rows):
    return [row_to_camelcase_edict(row) for row in rows]


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
