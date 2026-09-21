from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from app.core.models import Condition, MarketObservation, PriceSource


SCHEMA = """
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

CREATE INDEX IF NOT EXISTS idx_market_device
ON market_observations(device_key, condition, observed_on);
"""


class Database:
    def __init__(self, path: str | Path = "data/valora.db") -> None:
        self.path = Path(path)

    def connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def add_observation(self, observation: MarketObservation) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO market_observations
                (device_key, condition, price, observed_on, source, sample_note, city, sold, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation.device_key,
                    observation.condition.value,
                    observation.price,
                    observation.observed_on.isoformat(),
                    observation.source.value,
                    observation.sample_note,
                    observation.city,
                    int(observation.sold),
                    observation.confidence,
                ),
            )
            return int(cursor.lastrowid)

    def list_observations(self, device_key: str) -> list[MarketObservation]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT device_key, condition, price, observed_on, source,
                       sample_note, city, sold, confidence
                FROM market_observations
                WHERE device_key = ?
                ORDER BY observed_on DESC
                """,
                (device_key,),
            ).fetchall()

        return [
            MarketObservation(
                device_key=row["device_key"],
                condition=Condition(row["condition"]),
                price=float(row["price"]),
                observed_on=__import__("datetime").date.fromisoformat(row["observed_on"]),
                source=PriceSource(row["source"]),
                sample_note=row["sample_note"],
                city=row["city"],
                sold=bool(row["sold"]),
                confidence=float(row["confidence"]),
            )
            for row in rows
        ]
