from __future__ import annotations
import sqlite3
from datetime import date
from pathlib import Path
from app.core.catalog import DeviceModel,DeviceVariant
from app.core.models import Condition,MarketObservation,PriceSource
SCHEMA="""
CREATE TABLE IF NOT EXISTS device_models(id TEXT PRIMARY KEY,brand TEXT NOT NULL,name TEXT NOT NULL,year INTEGER,aliases TEXT NOT NULL DEFAULT '',active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS device_variants(id INTEGER PRIMARY KEY AUTOINCREMENT,model_id TEXT NOT NULL REFERENCES device_models(id) ON DELETE CASCADE,model_number TEXT NOT NULL DEFAULT '',ram_options TEXT NOT NULL DEFAULT '',storage_options TEXT NOT NULL DEFAULT '',aliases TEXT NOT NULL DEFAULT '',region TEXT NOT NULL DEFAULT '',active INTEGER NOT NULL DEFAULT 1);
CREATE INDEX IF NOT EXISTS idx_device_models_brand ON device_models(brand,name);
CREATE INDEX IF NOT EXISTS idx_device_variants_model ON device_variants(model_id);
CREATE TABLE IF NOT EXISTS market_observations(id INTEGER PRIMARY KEY AUTOINCREMENT,device_key TEXT NOT NULL,condition TEXT NOT NULL,price REAL NOT NULL CHECK(price>=0),observed_on TEXT NOT NULL,source TEXT NOT NULL,sample_note TEXT NOT NULL DEFAULT '',city TEXT NOT NULL DEFAULT '',sold INTEGER NOT NULL DEFAULT 0,confidence REAL NOT NULL DEFAULT 1.0 CHECK(confidence>=0 AND confidence<=1),market_type TEXT NOT NULL DEFAULT 'second_life');
CREATE INDEX IF NOT EXISTS idx_market_device ON market_observations(device_key,condition,market_type,observed_on);
"""
def _csv(values:tuple[object,...])->str:return ",".join(str(v) for v in values)
def _ints(value:str)->tuple[int,...]:return tuple(int(x) for x in value.split(",") if x)
class Database:
    def __init__(self,path:str|Path="data/valora.db")->None:self.path=Path(path)
    def connect(self)->sqlite3.Connection:
        self.path.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; c.execute("PRAGMA foreign_keys=ON"); return c
    def initialize(self)->None:
        with self.connect() as c:
            c.executescript(SCHEMA)
            columns={row["name"] for row in c.execute("PRAGMA table_info(market_observations)").fetchall()}
            if "market_type" not in columns: c.execute("ALTER TABLE market_observations ADD COLUMN market_type TEXT NOT NULL DEFAULT 'second_life'")
            c.execute("CREATE INDEX IF NOT EXISTS idx_market_device ON market_observations(device_key,condition,market_type,observed_on)")
    def add_device_model(self,model:DeviceModel)->None:
        with self.connect() as c:
            c.execute("INSERT OR REPLACE INTO device_models(id,brand,name,year,aliases,active) VALUES(?,?,?,?,?,?)",(model.id,model.brand,model.name,model.year,_csv(model.aliases),int(model.active)))
            c.execute("DELETE FROM device_variants WHERE model_id=?",(model.id,))
            for v in model.variants:c.execute("INSERT INTO device_variants(model_id,model_number,ram_options,storage_options,aliases,region,active) VALUES(?,?,?,?,?,?,?)",(model.id,v.model_number,_csv(v.ram_options_gb),_csv(v.storage_options_gb),_csv(v.aliases),v.region,int(v.active)))
    def list_device_models(self,brand:str|None=None)->list[DeviceModel]:
        q="SELECT * FROM device_models WHERE active=1"; p=()
        if brand:q+=" AND lower(brand)=lower(?)";p=(brand,)
        q+=" ORDER BY brand,name"
        with self.connect() as c:
            rows=c.execute(q,p).fetchall(); result=[]
            for row in rows:
                vs=c.execute("SELECT * FROM device_variants WHERE model_id=? AND active=1 ORDER BY model_number",(row["id"],)).fetchall()
                result.append(DeviceModel(row["id"],row["brand"],row["name"],row["year"],tuple(filter(None,row["aliases"].split(","))),tuple(DeviceVariant(v["model_id"],v["model_number"],_ints(v["ram_options"]),_ints(v["storage_options"]),tuple(filter(None,v["aliases"].split(","))),v["region"],bool(v["active"])) for v in vs),bool(row["active"])))
            return result
    def add_observation(self,observation:MarketObservation)->int:
        with self.connect() as c:
            cur=c.execute("INSERT INTO market_observations(device_key,condition,price,observed_on,source,sample_note,city,sold,confidence,market_type) VALUES(?,?,?,?,?,?,?,?,?,?)",(observation.device_key,observation.condition.value,observation.price,observation.observed_on.isoformat(),observation.source.value,observation.sample_note,observation.city,int(observation.sold),observation.confidence,observation.market_type));return int(cur.lastrowid)
    def list_observations(self,device_key:str)->list[MarketObservation]:
        with self.connect() as c: rows=c.execute("SELECT device_key,condition,price,observed_on,source,sample_note,city,sold,confidence,market_type FROM market_observations WHERE device_key=? ORDER BY observed_on DESC",(device_key,)).fetchall()
        return [MarketObservation(row["device_key"],Condition(row["condition"]),float(row["price"]),date.fromisoformat(row["observed_on"]),PriceSource(row["source"]),row["sample_note"],row["city"],bool(row["sold"]),float(row["confidence"]),row["market_type"]) for row in rows]
