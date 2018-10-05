from easydict import EasyDict as edict
from stringcase import camelcase, snakecase
from .linq import group_by, first_or_default


def dict_to_camelcase_edict(dct):
    return edict({camelcase(k): v for k, v in dct.items()})


async def aiterable_to_camelcase_edict(aiterable):
    return [dict_to_camelcase_edict(document.to_dict()) async for document in aiterable]


def dict_to_camelcase(dct):
    return {camelcase(k): v for k, v in dct.items()}


def dict_to_snakecase(dct):
    return {snakecase(k): v for k, v in dct.items()}


async def organise(aiterable, keys, field, is_single):
    camelcased = await aiterable_to_camelcase_edict(aiterable)
    field = camelcase(field)
    groups = group_by(camelcased, lambda row: row[field])
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


async def resolver_wrapper(func, *args, **kwargs):
    return await func(*args, **kwargs)


async def resolve_with_loader(loader, context, key, default=None):
    result = await context['request'].app['data_loaders'][loader].load(key)
    return result or default
