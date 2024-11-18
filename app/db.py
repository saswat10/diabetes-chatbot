
import os
from dotenv import load_dotenv
import motor.motor_asyncio


load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_DB"])
db = client.get_database("college")
print(db)