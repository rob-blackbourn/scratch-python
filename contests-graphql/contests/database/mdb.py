async def get_counts(mongo_db, user_id, field_name):
    counts = await mongo_db.users.find_one({'userId': user_id})
    return counts[field_name]
