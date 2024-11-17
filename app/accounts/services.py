async def get_current_user(email, db):
    return await db["users"].find_one({"email": email})
