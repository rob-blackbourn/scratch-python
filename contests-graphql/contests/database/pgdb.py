from easydict import EasyDict as edict
from stringcase import camelcase


def row_to_camelcase_edict(row):
    return edict({camelcase(k): v for k, v in row.items()})


def rows_to_camelcase_edict(rows):
    return [row_to_camelcase_edict(row) for row in rows]


def get_pool_from_context(context):
    return context['request'].app['pg_pool']


async def get_user(obj, info, **kwargs):
    pool = get_pool_from_context(info.context)

    async with pool.acquire() as connection:
        row = await connection.fetchrow('select * from users where api_key = $1', kwargs['key'])
    if not row:
        raise ValueError('Not found')
    return row_to_camelcase_edict(row)


async def get_contests(obj, info, **kwargs):
    pool = get_pool_from_context(info.context)

    async with pool.acquire() as connection:
        rows = await connection.fetch('select * from contests where created_by = $1', obj.id)
    return rows_to_camelcase_edict(rows)