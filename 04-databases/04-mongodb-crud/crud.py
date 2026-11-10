# ─────────────────────────────────────────────────────────────
# Lesson: MongoDB CRUD
#
# Notice:
#   - no schema file
#   - `_id` is auto-generated (ObjectId) — we convert to str for JSON
#   - partial update = just send the fields you want to change
# ─────────────────────────────────────────────────────────────

import os
from bson import ObjectId
from pymongo import MongoClient

client = MongoClient(os.environ.get("MONGODB_URL", "mongodb://localhost:27017"))
users = client["playbook"]["users"]


def _to_json(doc) -> dict:
    return {"id": str(doc["_id"]), "name": doc["name"], "email": doc["email"]}


def create_user(name: str, email: str) -> dict:
    result = users.insert_one({"name": name, "email": email})
    return {"id": str(result.inserted_id), "name": name, "email": email}


def get_user(user_id: str) -> dict | None:
    doc = users.find_one({"_id": ObjectId(user_id)})
    return None if doc is None else _to_json(doc)


def update_user(user_id: str, patch: dict) -> dict | None:
    allowed = {"name", "email"}
    clean = {k: v for k, v in patch.items() if k in allowed}
    if clean:
        users.update_one({"_id": ObjectId(user_id)}, {"$set": clean})
    return get_user(user_id)


def delete_user(user_id: str) -> bool:
    result = users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0


if __name__ == "__main__":
    u = create_user("Rakibul", "rakibul@example.com")
    print("created:", u)
    print("get:", get_user(u["id"]))
    print("update:", update_user(u["id"], {"name": "Rakibul Islam"}))
    print("delete:", delete_user(u["id"]))
    print("get after delete:", get_user(u["id"]))