from ..utils.asyncpg import select_from_table_by_key


async def get_users_by_api_keys(pool, api_keys):
    return await select_from_table_by_key(pool, 'users', 'api_key', True, api_keys)


async def get_users_by_ids(pool, ids):
    return await select_from_table_by_key(pool, 'users', 'id', True, ids)


async def get_contests_by_created_bys(pool, created_bys):
    return await select_from_table_by_key(pool, 'contests', 'created_by', False, created_bys)


async def get_names_by_contest_ids(pool, contest_ids):
    return await select_from_table_by_key(pool, 'names', 'contest_id', False, contest_ids)
