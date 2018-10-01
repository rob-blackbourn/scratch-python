async def resolver_wrapper(func, *args, **kwargs):
    return await func(*args, **kwargs)
