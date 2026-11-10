# ─────────────────────────────────────────────────────────────
# Lesson: DynamoDB CRUD
#
# The big difference from SQL: the table is created with an explicit
# key schema, and every read/write must go through that key.
#
# Notice how `update_user` builds an UpdateExpression instead of a
# SQL string — DynamoDB never takes raw SQL. Every part of the update
# (field names, values, expression) is passed separately.
# ─────────────────────────────────────────────────────────────

import os
import uuid
import boto3

ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT")  # None = real AWS
REGION = os.environ.get("AWS_REGION", "us-east-1")
TABLE = os.environ.get("DYNAMODB_TABLE", "playbook-users")

dynamodb = boto3.resource("dynamodb", region_name=REGION, endpoint_url=ENDPOINT)


def _table():
    try:
        t = dynamodb.create_table(
            TableName=TABLE,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        t.wait_until_exists()
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        pass
    return dynamodb.Table(TABLE)


def create_user(name: str, email: str) -> dict:
    user = {"id": str(uuid.uuid4()), "name": name, "email": email}
    _table().put_item(Item=user)
    return user


def get_user(user_id: str) -> dict | None:
    resp = _table().get_item(Key={"id": user_id})
    return resp.get("Item")


def update_user(user_id: str, patch: dict) -> dict | None:
    allowed = {"name", "email"}
    clean = {k: v for k, v in patch.items() if k in allowed}
    if not clean:
        return get_user(user_id)
    # Build an UpdateExpression — DynamoDB never takes raw SQL.
    expr = "SET " + ", ".join(f"#f{i} = :v{i}" for i in range(len(clean)))
    names = {f"#f{i}": k for i, k in enumerate(clean)}
    values = {f":v{i}": v for i, v in enumerate(clean.values())}
    _table().update_item(
        Key={"id": user_id},
        UpdateExpression=expr,
        ExpressionAttributeNames=names,
        ExpressionAttributeValues=values,
    )
    return get_user(user_id)


def delete_user(user_id: str) -> bool:
    _table().delete_item(Key={"id": user_id})
    return True  # DynamoDB delete is idempotent


if __name__ == "__main__":
    u = create_user("Rakibul", "rakibul@example.com")
    print("created:", u)
    print("get:", get_user(u["id"]))
    print("update:", update_user(u["id"], {"name": "Rakibul Islam"}))
    print("delete:", delete_user(u["id"]))
    print("get after delete:", get_user(u["id"]))