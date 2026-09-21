from __future__ import annotations

from .database import Database
from app.core.catalog import demo_catalog


def seed_catalog(database: Database) -> int:
    catalog = demo_catalog()
    count = 0
    for model in catalog.models:
        database.add_device_model(model)
        count += 1
    return count
