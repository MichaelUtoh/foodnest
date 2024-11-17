import motor.motor_asyncio
from decouple import config

DATABASE_URL = config("MONGO_DB_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client.foodnest_db


async def init_db():
    print("Database connected")


def get_database():
    return db
