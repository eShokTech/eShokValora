from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from app.core.catalog import DeviceModel, DeviceVariant
from app.core.models import Condition, MarketObservation, PriceSource

SCHEMA = """
CREATE TABLE IF NOT EXISTS device_models (
    id TEXT PRIMARY KEY,
    brand TEXT NOT NULL,
    name TEXT NOT NULL,
    year INTEGER,
    aliases TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS device_variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id TEXT NOT NULL REFERENCES device_models(id) ON DELETE CASCADE,
    model_number TEXT NOT NULL DEFAULT '',
    ram_options TEXT NOT NULL DEFAULT '',
    storage_options TEXT NOT NULL DEFAULT '',
    aliases TEXT NOT NULL DEFAULT '',
    region TEXT NOT NULL DEFAULT '',
    active INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_device_models_brand ON device_models(brand, name);
CREATE INDEX IF NOT EXISTS idx_device_variants_model ON device_variants(model_id);
CREATE TABLE IF NOT EXISTS market_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_key TEXT NOT NULL,
    condition TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0),
    observed_on TEXT NOT NULL,
    source TEXT NOT NULL,
    sample_note TEXT NOT NULL DEFAULT '',
    city TEXT NOT NULL DEFAULT '',
    sold INTEGER NOT NULL DEFAULT 0,
    confidence REAL NOT NULL DEFAULT 1.0 CHECK(confidence >= 0 AND confidence <= 1)
);
CREATE INDEX IF NOT EXISTS idx_market_device ON market_observations(device_key, condition, observed_on);
"""

def _csv(values: tuple[object, ...]) -> str:
    return ",".join(str(value) for value in values)

def _ints(value: str) -> tuple[int, ...]:
    return tuple(int(item) for item in value.split(",") if item)

class Database:
    def __init__(self, path: str | Path = "data/valora.db") -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def add_device_model(self, model: DeviceModel) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO device_models (id, brand, name, year, aliases, active) VALUES (?, ?, ?, ?, ?, ?)",
                (model.id, model.brand, model.name, model.year, _csv(model.aliases), int(model.active)),
            )
            connection.execute("DELETE FROM device_variants WHERE model_id = ?", (model.id,))
            for variant in model.variants:
                connection.execute(
                    "INSERT INTO device_variants (model_id, model_number, ram_options, storage_options, aliases, region, active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (model.id, variant.model_number, _csv(variant.ram_options_gb), _csv(variant.storage_options_gb), _csv(variant.aliases), variant.region, int(variant.active)),
                )

    def list_device_models(self, brand: str | None = None) -> list[DeviceModel]:
        query = "SELECT * FROM device_models WHERE active = 1"
        params: tuple[object, ...] = ()
        if brand:
            query += " AND lower(brand) = lower(?)"
            params = (brand,)
        query += " ORDER BY brand, name"
        with self.connect() as connection:
            rows = connection.execute(query, params).fetchall()
            models: list[DeviceModel] = []
            for row in rows:
                variants = connection.execute(
                    "SELECT * FROM device_variants WHERE model_id = ? AND active = 1 ORDER BY model_number",
                    (row["id"],),
                ).fetchall()
                models.append(DeviceModel(
                    id=row["id"], brand=row["brand"], name=row["name"], year=row["year"],
                    aliases=tuple(filter(None, row["aliases"].split(","))),
                    variants=tuple(DeviceVariant(
                        model_id=v["model_id"], model_number=v["model_number"],
                        ram_options_gb=_ints(v["ram_options"]), storage_options_gb=_ints(v["storage_options"]),
                        aliases=tuple(filter(None, v["aliases"].split(","))), region=v["region"], active=bool(v["active"])
                    ) for v in variants),
                    active=bool(row["active"])
                ))
            return models

    def add_observation(self, observation: MarketObservation) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO market_observations (device_key, condition, price, observed_on, source, sample_note, city, sold, confidence) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (observation.device_key, observation.condition.value, observation.price, observation.observed_on.isoformat(),
                 observation.source.value, observation.sample_note, observation.city, int(observation.sold), observation.confidence),
            )
            return int(cursor.lastrowid)

    def list_observations(self, device_key: str) -> list[MarketObservation]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT device_key, condition, price, observed_on, source, sample_note, city, sold, confidence FROM market_observations WHERE device_key = ? ORDER BY observed_on DESC",
                (device_key,),
            ).fetchall()
        return [MarketObservation(
            device_key=row["device_key"], condition=Condition(row["condition"]), price=float(row["price"]),
            observed_on=date.fromisoformat(row["observed_on"]), source=PriceSource(row["source"]),
            sample_note=row["sample_note"], city=row["city"], sold=bool(row["sold"]), confidence=float(row["confidence"])
        ) for row in rows]
