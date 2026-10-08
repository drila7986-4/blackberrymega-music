from datetime import datetime, timezone, timedelta
from db import coins_col, game_users_col
from pymongo import ReturnDocument

async def get_coins(user_id: int) -> int:
    doc = await coins_col.find_one({"_id": int(user_id)})
    return int(doc.get("coins", 0)) if doc else 0

async def add_coins(user_id: int, amount: int) -> int:
    result = await coins_col.find_one_and_update(
        {"_id": int(user_id)}, {"$inc": {"coins": int(amount)}},
        upsert=True, return_document=ReturnDocument.AFTER,
    )
    return int(result.get("coins", 0)) if result else await get_coins(user_id)

async def top_coins(limit: int = 10):
    cursor = coins_col.find({"coins": {"$gt": 0}}).sort("coins", -1).limit(limit)
    return await cursor.to_list(length=limit)

async def mark_game_user_started(user_id: int) -> None:
    await game_users_col.update_one({"_id": int(user_id)}, {"$set": {"started": True}}, upsert=True)

async def has_started_in_dm(user_id: int) -> bool:
    doc = await game_users_col.find_one({"_id": int(user_id), "started": True})
    return bool(doc)

async def claim_daily(user_id: int):
    now = datetime.now(timezone.utc)
    doc = await coins_col.find_one({"_id": int(user_id)})
    last = doc.get("daily_claim") if doc else None
    if last:
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        remaining = timedelta(hours=24) - (now - last)
        if remaining.total_seconds() > 0:
            return False, max(1, int(remaining.total_seconds() // 3600)), await get_coins(user_id)
    result = await coins_col.find_one_and_update(
        {"_id": int(user_id)},
        {"$inc": {"coins": 500}, "$set": {"daily_claim": now}},
        upsert=True, return_document=ReturnDocument.AFTER,
    )
    return True, 0, int(result.get("coins", 0))
