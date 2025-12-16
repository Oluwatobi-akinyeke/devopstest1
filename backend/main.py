from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
import uvicorn
import certifi
import logging
from datetime import datetime, timezone
import os
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()  # Load environment variables from .env

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MongoDB connection variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

CA_FILE = certifi.where()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ...
    client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=CA_FILE)
# MongoDB client (initialized in lifespan)
client = None
db = None
items_collection = None


def convert_objectid(document: dict) -> dict:
    """
    Converts MongoDB's ObjectId to string in a document.
    """
    document["_id"] = str(document["_id"])
    return document


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, items_collection
    client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=CA_FILE)
    db = client[DB_NAME]
    items_collection = db[COLLECTION_NAME]
    logger.info("Connected to MongoDB using verified SSL.")
    yield
    client.close()
    logger.info("MongoDB connection closed.")


app = FastAPI(
    title="Item Service",
    description="A robust FastAPI service for managing items with MongoDB backend.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Or ["GET", "POST", "PUT", "DELETE"]
    allow_headers=["*"],
)

class Item(BaseModel):
    name: str
    description: str | None = None


ITEM_NOT_FOUND_MSG = "Item not found"


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    logger.info("Health check requested.")
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/items", status_code=status.HTTP_200_OK)
async def get_all_items():
    logger.info("Retrieving all items from MongoDB.")
    items_cursor = items_collection.find()
    items = await items_cursor.to_list(length=None)
    return {"items": [convert_objectid(item) for item in items]}


@app.get("/items/{item_name}", status_code=status.HTTP_200_OK)
async def get_item(item_name: str):
    item = await items_collection.find_one({"name": item_name})
    if not item:
        logger.warning(f"Item not found: {item_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ITEM_NOT_FOUND_MSG
        )
    logger.info(f"Item retrieved: {item_name}")
    return {"item": convert_objectid(item)}


@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    existing = await items_collection.find_one({"name": item.name})
    if existing:
        logger.warning(f"Duplicate item creation attempted: {item.name}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Item with this name already exists",
        )
    result = await items_collection.insert_one(item.model_dump())
    created_item = await items_collection.find_one({"_id": result.inserted_id})
    logger.info(f"Item created: {item.name}")
    return {
        "message": "Item created successfully",
        "item": convert_objectid(created_item),
    }


@app.put("/items/{item_name}", status_code=status.HTTP_200_OK)
async def update_item(item_name: str, updated_item: Item):
    result = await items_collection.update_one(
        {"name": item_name}, {"$set": updated_item.model_dump()}
    )
    if result.matched_count == 0:
        logger.warning(f"Update failed. Item not found: {item_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ITEM_NOT_FOUND_MSG
        )

    updated = await items_collection.find_one({"name": updated_item.name})
    logger.info(f"Item updated: {item_name}")
    return {"message": "Item updated successfully", "item": convert_objectid(updated)}


@app.delete("/items/{item_name}", status_code=status.HTTP_200_OK)
async def delete_item(item_name: str):
    item = await items_collection.find_one({"name": item_name})
    if not item:
        logger.warning(f"Delete failed. Item not found: {item_name}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=ITEM_NOT_FOUND_MSG
        )

    await items_collection.delete_one({"name": item_name})
    logger.info(f"Item deleted: {item_name}")
    return {"message": "Item deleted successfully", "item": convert_objectid(item)}


if __name__ == "__main__":  # pragma: no cover
    port = int(os.getenv("PORT", 8000))  # fallback to 8000 if not set
    uvicorn.run(app, host="0.0.0.0", port=port)  # pragma: no cover
