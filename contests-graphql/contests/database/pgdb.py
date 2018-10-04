from ..utils.asyncpg import select_from_table_by_key, row_to_camelcase_edict
import re


def slugify(text):
    return re.sub(r'\W+', '-', text.lower())


async def get_users_by_api_keys(pool, api_keys):
    return await select_from_table_by_key(pool, 'users', 'api_key', True, api_keys)


async def get_users_by_ids(pool, ids):
    return await select_from_table_by_key(pool, 'users', 'id', True, ids)


async def get_contests_by_created_bys(pool, created_bys):
    return await select_from_table_by_key(pool, 'contests', 'created_by', False, created_bys)


async def get_names_by_contest_ids(pool, contest_ids):
    return await select_from_table_by_key(pool, 'names', 'contest_id', False, contest_ids)


async def add_new_contest(pool, input):
    code = slugify(input['title'])

    async with pool.acquire() as connection:
        row = await connection.fetchrow(
            '''
insert into contests(code, title, description, created_by)
values ($1, $2, $3,
  (select id from users where api_key = $4))
returning *''',
            code,
            input['title'],
            input['description'],
            input['apiKey'])
    result = row_to_camelcase_edict(row)
    return result
