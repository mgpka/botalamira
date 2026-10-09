# database.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# المجموعات في قاعدة البيانات
groups_col = db["groups"]
users_col = db["users"]
settings_col = db["settings"]

async def ping_db():
    """فحص الاتصال بقاعدة البيانات عند الإقلاع"""
    try:
        await client.admin.command('ping')
        return True
    except Exception as e:
        print(f"❌ خطأ بقاعدة البيانات: {e}")
        return False

# إدارة المجموعات
async def is_group_active(chat_id: int) -> bool:
    doc = await groups_col.find_one({"chat_id": chat_id})
    return bool(doc and doc.get("active", False))

async def set_group_status(chat_id: int, title: str, status: bool):
    await groups_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"chat_id": chat_id, "title": title, "active": status}},
        upsert=True
    )

async def set_lock(chat_id: int, lock_name: str, state: bool):
    await groups_col.update_one(
        {"chat_id": chat_id},
        {"$set": {f"locks.{lock_name}": state}},
        upsert=True
    )

async def get_locks(chat_id: int) -> dict:
    doc = await groups_col.find_one({"chat_id": chat_id})
    if doc and "locks" in doc:
        return doc["locks"]
    return {
        "links": True,
        "photos": False,
        "stickers": False,
        "forward": False,
        "spam": True
    }

# إدارة نقاط وبنك الأعضاء
async def get_user_profile(user_id: int) -> dict:
    user = await users_col.find_one({"user_id": user_id})
    if not user:
        user = {
            "user_id": user_id,
            "points": 50,
            "bank": 1000,
            "messages": 0
        }
        await users_col.insert_one(user)
    return user

async def add_user_points(user_id: int, amount: int):
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"points": amount}},
        upsert=True
    )

async def add_user_messages(user_id: int, count: int = 1):
    await users_col.update_one(
        {"user_id": user_id},
        {"$inc": {"messages": count}},
        upsert=True
    )
