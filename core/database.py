from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from typing import Optional
import os


class Database:
    client: Optional[MongoClient] = None
    async_client: Optional[AsyncIOMotorClient] = None


db = Database()


def get_database_url() -> str:
    host = os.getenv("MONGO_HOST", "localhost")
    port = os.getenv("MONGO_PORT", "27017")
    user = os.getenv("MONGO_USER", "")
    password = os.getenv("MONGO_PASSWORD", "")
    db_name = os.getenv("MONGO_DB", "aiqrh")
    
    if user and password:
        return f"mongodb://{user}:{password}@{host}:{port}/{db_name}"
    return f"mongodb://{host}:{port}/{db_name}"


def init_mongodb():
    db.client = MongoClient(get_database_url())
    return db.client


def get_db():
    if db.client is None:
        init_mongodb()
    return db.client[os.getenv("MONGO_DB", "aiqrh")]


async def init_async_mongodb():
    db.async_client = AsyncIOMotorClient(get_database_url())
    return db.async_client


async def get_async_db():
    if db.async_client is None:
        await init_async_mongodb()
    return db.async_client[os.getenv("MONGO_DB", "aiqrh")]


def close_mongodb():
    if db.client:
        db.client.close()
    if db.async_client:
        db.async_client.close()
