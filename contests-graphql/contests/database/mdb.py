def get_mongo_db_from_context(context):
    return context['request'].app['mongo_db']


async def get_counts(obj, info, **kwargs):
    mongo_db = get_mongo_db_from_context(info.context)

    counts = await mongo_db.users.find_one({'userId': obj.id})
    return counts[info.field_name]
