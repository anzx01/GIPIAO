from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
from api.config import get_settings


settings = get_settings()


class Database:
    client: Optional[MongoClient] = None
    async_client: Optional[AsyncIOMotorClient] = None


db = Database()


def get_database_url() -> str:
    return settings.database.connection_string


def init_mongodb():
    db.client = MongoClient(get_database_url())
    return db.client


def get_db():
    if db.client is None:
        init_mongodb()
    return db.client[settings.database.db_name]


async def init_async_mongodb():
    db.async_client = AsyncIOMotorClient(get_database_url())
    return db.async_client


async def get_async_db():
    if db.async_client is None:
        await init_async_mongodb()
    return db.async_client[settings.database.db_name]


def close_mongodb():
    if db.client:
        db.client.close()
    if db.async_client:
        db.async_client.close()
