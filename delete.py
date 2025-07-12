from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["skill_swap_db"]
result = db.users.delete_many({})
print(f"Deleted {result.deleted_count} users.")
