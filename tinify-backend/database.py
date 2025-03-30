from motor.motor_asyncio import AsyncIOMotorClient
# from pymongo import MongoClient

from config import DB_NAME, MONGO_URI

# Establish MongoDb Connection
# client = MongoClient(MONGO_URI)
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collections
SHORT_TO_LONG_COLL = db['short_to_long']
URLS_STATS_COLL = db['url_stats']

# Ensure indexing for faster lookups
SHORT_TO_LONG_COLL.create_index("short_id", unique=True)
URLS_STATS_COLL.create_index("short_id", unique=True)