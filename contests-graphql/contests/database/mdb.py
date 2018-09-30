async def get_counts(obj, info, **kwargs):
    counts = await info.context['mongo_db'].users.find_one({'userId': obj.id})
    return counts[info.field_name]
