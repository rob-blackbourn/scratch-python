async def resolver_wrapper(func, *args, **kwargs):
    return await func(*args, **kwargs)


async def resolve_with_loader(loader, context, key, default=None):
    result = await context['request'].app['data_loaders'][loader].load(key)
    return result or default
