from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "chatbot_db"

class MongoDB:
    def __init__(self):
        self.client = None

    async def connect(self):
        """Initialize MongoDB connection."""
        self.client = AsyncIOMotorClient(MONGO_URI)
        print("Connected to MongoDB.")

    async def disconnect(self):
        """Close MongoDB connection."""
        self.client.close()
        print("Disconnected from MongoDB.")

    @asynccontextmanager
    async def get_collection(self, collection_name: str):
        """Context manager for accessing a MongoDB collection."""
        db = self.client[DB_NAME]
        collection = db[collection_name]
        try:
            yield collection
        finally:
            pass  # Additional cleanup logic if needed

mongodb = MongoDB()
