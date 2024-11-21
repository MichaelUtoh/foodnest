from bson import ObjectId
from typing import Any


def transform_mongo_data(data: Any) -> Any:
    """
    Recursively transforms MongoDB data, converting ObjectId to string.
    """
    if isinstance(data, list):
        return [transform_mongo_data(item) for item in data]
    if isinstance(data, dict):
        return {key: transform_mongo_data(value) for key, value in data.items()}
    if isinstance(data, ObjectId):
        return str(data)
    return data
