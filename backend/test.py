import pytest
from fastapi.testclient import TestClient
import mongomock
from main import app
import main  # for patching global variable
from motor.motor_asyncio import AsyncIOMotorClient


# Async wrapper for mongomock collection
class AsyncIOMotorMockCollection:
    def __init__(self, collection):
        self._collection = collection

    def find(self, *args, **kwargs):
        docs = list(self._collection.find(*args, **kwargs))

        class AsyncCursor:
            async def to_list(self, length=None):
                return docs

        return AsyncCursor()

    async def find_one(self, *args, **kwargs):
        return self._collection.find_one(*args, **kwargs)

    async def insert_one(self, document):
        result = self._collection.insert_one(document)

        class Result:
            inserted_id = result.inserted_id

        return Result()

    async def update_one(self, filter, update):
        result = self._collection.update_one(filter, update)

        class Result:
            matched_count = result.matched_count

        return Result()

    async def delete_one(self, filter):
        result = self._collection.delete_one(filter)

        class Result:
            deleted_count = result.deleted_count

        return Result()

    async def delete_many(self, filter):
        result = self._collection.delete_many(filter)

        class Result:
            deleted_count = result.deleted_count

        return Result()


# Setup mock MongoDB
mock_client = mongomock.MongoClient()
mock_db = mock_client["testdb"]
mock_collection = mock_db["items"]
async_mock_collection = AsyncIOMotorMockCollection(mock_collection)

# Patch global reference in main.py
main.items_collection = async_mock_collection

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    mock_collection.delete_many({})
    mock_collection.insert_many(
        [
            {"name": "item1", "description": "First item"},
            {"name": "item2", "description": "Second item"},
        ]
    )
    yield
    mock_collection.delete_many({})


# --- Health Check Tests ---
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()


# --- Get All Items Tests ---


def test_get_all_items_initial():
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 2
    item_names = [item["name"] for item in response.json()["items"]]
    assert "item1" in item_names
    assert "item2" in item_names


def test_get_all_items_empty():
    mock_collection.delete_many({})
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json()["items"] == []


# --- Create Item Tests ---
def test_create_item_success():
    new_item = {"name": "test_item", "description": "This is a test item"}
    response = client.post("/items", json=new_item)
    assert response.status_code == 201
    assert response.json()["message"] == "Item created successfully"
    assert response.json()["item"]["name"] == "test_item"
    assert response.json()["item"]["description"] == "This is a test item"

    # Verify item exists after creation
    get_response = client.get("/items/test_item")
    assert get_response.status_code == 200
    assert get_response.json()["item"]["name"] == "test_item"


def test_create_item_duplicate():
    duplicate_item = {"name": "item1", "description": "First item"}
    response = client.post("/items", json=duplicate_item)
    assert response.status_code == 409
    assert "Item with this name already exists" in response.json()["detail"]


def test_create_item_invalid_data_wrong_type():
    wrong_type_item = {"name": 123, "description": "invalid name type"}
    response = client.post("/items", json=wrong_type_item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]
    assert response.json()["detail"][0]["type"] == "string_type"
    assert "Input should be a valid string" in response.json()["detail"][0]["msg"]


def test_create_item_invalid_data_missing_required_field():
    missing_name_item = {"description": "This item is missing a name"}
    response = client.post("/items", json=missing_name_item)
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "name"]
    assert response.json()["detail"][0]["type"] == "missing"
    assert "Field required" in response.json()["detail"][0]["msg"]


# --- Get Single Item Tests ---


def test_get_item_existing():
    response = client.get("/items/item1")
    assert response.status_code == 200
    assert response.json()["item"]["name"] == "item1"


def test_get_item_not_found():
    response = client.get("/items/non_existent_item")
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


# --- Update Item Tests ---


def test_update_item_success():
    update_data = {"name": "item1", "description": "Updated description for item1"}
    response = client.put("/items/item1", json=update_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Item updated successfully"
    assert response.json()["item"]["description"] == "Updated description for item1"

    # Verify update
    get_response = client.get("/items/item1")
    assert get_response.status_code == 200
    assert get_response.json()["item"]["description"] == "Updated description for item1"


def test_update_item_not_found():
    update_data = {"name": "non_existent", "description": "Should not update"}
    response = client.put("/items/another_non_existent", json=update_data)
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


def test_update_item_invalid_data():
    invalid_update = {"description": "just a description"}  # Missing 'name'
    response = client.put("/items/item1", json=invalid_update)
    assert response.status_code == 422


def test_update_item_name_mismatch():
    update_data = {"name": "mismatch_name", "description": "desc"}
    response = client.put("/items/item1", json=update_data)
    assert response.status_code == 200
    # Optionally, check updated data
    assert response.json()["item"]["name"] == "mismatch_name"


# --- Delete Item Tests ---


def test_delete_item_success():
    # Ensure there's an item to delete by creating an item
    client.post("/items", json={"name": "item_to_delete", "description": "Temp item"})

    response = client.delete("/items/item_to_delete")
    assert response.status_code == 200
    assert response.json()["message"] == "Item deleted successfully"

    # Verify item is deleted
    get_response = client.get("/items/item_to_delete")
    assert get_response.status_code == 404
    assert "Item not found" in get_response.json()["detail"]


def test_delete_item_not_found():
    response = client.delete("/items/definitely_not_here")
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]
