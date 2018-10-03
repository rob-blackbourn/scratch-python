from easydict import EasyDict as edict
from stringcase import camelcase
from .linq import group_by, first_or_default


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


async def select_from_table_by_key(pool, table, field, is_single, keys):
    async with pool.acquire() as connection:
        rows = await connection.fetch(f'select * from {table} where {field} = ANY($1)', keys)
    return organise(rows, keys, camelcase(field), is_single)
