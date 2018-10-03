from easydict import EasyDict as edict
from stringcase import camelcase
from ..utils.linq import group_by, first_or_default


def row_to_camelcase_edict(row):
    return edict({camelcase(k): v for k, v in row.items()})


def rows_to_camelcase_edict(rows):
    return [row_to_camelcase_edict(row) for row in rows]


def organise(rows, keys, field, is_single):
    camelcase_rows = rows_to_camelcase_edict(rows)
    groups = group_by(camelcase_rows, lambda row: row[field])
    result = []
    for key in keys:
        values = groups.get(key)
        if values:
            if is_single:
                result.append(first_or_default(values))
            else:
                result.append(values)
        else:
            result.append(None)

    return result


async def get_user_by_api_key(pg_pool, api_key):
    async with pg_pool.acquire() as connection:
        row = await connection.fetchrow('select * from users where api_key = $1', api_key)
    if not row:
        raise ValueError('Not found')
    return row_to_camelcase_edict(row)


async def get_users_by_api_keys(pg_pool, api_keys):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from users where api_key = ANY($1)', api_keys)
    return organise(rows, api_keys, 'apiKey', True)


async def get_user_by_id(pg_pool, id):
    async with pg_pool.acquire() as connection:
        row = await connection.fetchrow('select * from users where id = $1', id)
    if not row:
        raise ValueError('Not found')
    return row_to_camelcase_edict(row)


async def get_users_by_ids(pg_pool, ids):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from users where id = ANY($1)', ids)
    return organise(rows, ids, 'id', True)


async def get_contests_by_created_by(pg_pool, created_by):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from contests where created_by = $1', created_by)
    return rows_to_camelcase_edict(rows)


async def get_contests_by_created_bys(pg_pool, created_bys):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from contests where created_by = ANY($1)', created_bys)
    return organise(rows, created_bys, 'createdBy', False)


async def get_names_by_contest_id(pg_pool, contest_id):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from names where contest_id = $1', contest_id)
    return rows_to_camelcase_edict(rows)


async def get_names_by_contest_ids(pg_pool, contest_ids):
    async with pg_pool.acquire() as connection:
        rows = await connection.fetch('select * from names where contest_id = ANY($1)', contest_ids)
    return organise(rows, contest_ids, 'contestId', False)
