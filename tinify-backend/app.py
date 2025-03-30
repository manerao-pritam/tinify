import datetime
import logging
import time
from datetime import timedelta, datetime

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_410_GONE
import asyncio

from config import SHORT_URL_LENGTH, DOMAIN_NAME, EXPIRE_IN_DAYS, REDIS_URI
from database import client, SHORT_TO_LONG_COLL, URLS_STATS_COLL
from models import URLToShorten
from utils.datetime_util import datetime_to_str
from utils.hash_util import get_hash, base62_encoding

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize Redis
redis_client = redis.from_url(REDIS_URI, decode_responses=True)

# Helper function to serialize MongoDB documents
def serialize_document(doc):
    """Convert MongoDB document to a JSON-serializable format."""
    doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    if "expiry" in doc:
        doc["expiry"] = datetime_to_str(doc["expiry"])
    return doc

@app.get('/')
async def get_all_urls():
    """Retrieve all shortened URLs."""
    urls = await SHORT_TO_LONG_COLL.find().to_list(None)
    return [serialize_document(row) for row in urls]

@app.post('/shorten')
async def shorten(data: URLToShorten):
    """Shorten a Long URL to a short URL."""
    url = str(data.url)

    # Generate hash and get first 8 characters
    url_hash = get_hash(url)
    shortened_id = base62_encoding(url_hash)[:SHORT_URL_LENGTH]

    # Check for existing short_id
    existing_doc = await SHORT_TO_LONG_COLL.find_one({"short_id": shortened_id})
    if existing_doc:
        if existing_doc['long_url'] == url:
            return {"message": "Success", "url": url, "short_url": f"{DOMAIN_NAME}/{shortened_id}"}
        url_hash = get_hash(url + str(time.time()))
        shortened_id = base62_encoding(url_hash)[:SHORT_URL_LENGTH]

    # Set expiry date
    expiry_date = datetime.utcnow() + timedelta(days=EXPIRE_IN_DAYS)

    # Insert into database
    row = {"short_id": shortened_id, "long_url": url, "expiry": expiry_date}
    await SHORT_TO_LONG_COLL.insert_one(row)

    logger.info(f"URL shortened: {url} -> {DOMAIN_NAME}/{shortened_id}")

    return {"message": "Success", "url": url, "short_url": f"{DOMAIN_NAME}/{shortened_id}"}

@app.get('/expand/{short_url}')
async def expand(short_url: str):
    """Expand a short URL to its original URL."""
    fetched = await SHORT_TO_LONG_COLL.find_one({"short_id": short_url})
    if not fetched:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Shortened URL not found")

    if 'expiry' in fetched and isinstance(fetched['expiry'], datetime):
        if fetched['expiry'] < datetime.utcnow():
            logger.warning(f"Shortened URL expired: {short_url}")
            raise HTTPException(status_code=HTTP_410_GONE, detail="Shortened URL has expired")

    logger.info(f"Expanding URL: {short_url} -> {fetched['long_url']}")
    return RedirectResponse(url=fetched["long_url"])

@app.get('/stats/{short_url}')
async def get_url_stats(short_url: str):
    """Fetch the short URL stats"""
    stats = await URLS_STATS_COLL.find_one({"short_id": short_url})
    if not stats:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Shortened URL not found")
    return serialize_document(stats)

@app.get('/redirect/{short_url}')
async def redirect(short_url: str):
    """Redirect user and track stats"""
    fetched = await SHORT_TO_LONG_COLL.find_one({"short_id": short_url})
    if not fetched:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Shortened URL not found")

    await redis_client.incr(f"short_url:{short_url}")
    return RedirectResponse(url=fetched["long_url"])

async def sync_redis_to_mongo():
    """Efficiently sync Redis counters to MongoDB periodically."""
    while True:
        try:
            keys = await redis_client.keys("short_url:*")
            if keys:
                counts = await redis_client.mget(keys)
                updates = [
                    URLS_STATS_COLL.update_one({"short_id": key.split(":")[1]}, {"$inc": {"access_count": int(count)}}, upsert=True)
                    for key, count in zip(keys, counts) if count is not None
                ]
                await asyncio.gather(*updates)
                await redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Error syncing Redis to MongoDB: {e}")
        await asyncio.sleep(60)

@app.on_event("startup")
async def start_sync():
    asyncio.create_task(sync_redis_to_mongo())

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()
    client.close()