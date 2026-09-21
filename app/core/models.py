from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional

class Condition(str, Enum):
    WORKING="working"; MINOR_DETAILS="minor_details"; DAMAGED="damaged"; FOR_PARTS="for_parts"; REFURBISHED="refurbished"
class PriceSource(str, Enum):
    MARKETPLACE="marketplace"; LOCAL="local"; USER_OPERATION="user_operation"; OTHER="other"
@dataclass(frozen=True)
class Device:
    brand:str; model:str; storage_gb:Optional[int]=None; ram_gb:Optional[int]=None; year:Optional[int]=None
    @property
    def key(self)->str:
        parts=[self.brand.strip().lower(),self.model.strip().lower()]
        if self.storage_gb: parts.append(f"{self.storage_gb}gb")
        if self.ram_gb: parts.append(f"{self.ram_gb}gb_ram")
        return "|".join(parts)
@dataclass(frozen=True)
class MarketObservation:
    device_key:str; condition:Condition; price:float; observed_on:date; source:PriceSource; sample_note:str=""; city:str=""; sold:bool=False; confidence:float=1.0; market_type:str="second_life"
    def __post_init__(self)->None:
        if self.price<0: raise ValueError("El precio no puede ser negativo.")
        if not 0<=self.confidence<=1: raise ValueError("La confianza debe estar entre 0 y 1.")
@dataclass(frozen=True)
class MarketEstimate:
    price:float; low:float; high:float; sample_count:int; confidence:float; condition:Condition; market_type:str="second_life"
@dataclass(frozen=True)
class ValuationInput:
    market_price:float; repair_cost:float=0.0; risk_reserve:float=0.0; selling_cost:float=0.0; other_cost:float=0.0; desired_profit:float=0.0; desired_margin_percent:Optional[float]=None; recommendation_buffer:float=0.0
    def __post_init__(self)->None:
        for name in ("market_price","repair_cost","risk_reserve","selling_cost","other_cost","desired_profit","recommendation_buffer"):
            if getattr(self,name)<0: raise ValueError(f"{name} no puede ser negativo.")
        if self.market_price<=0: raise ValueError("El precio de mercado debe ser mayor que cero.")
        if self.desired_margin_percent is not None and not 0<=self.desired_margin_percent<100: raise ValueError("El margen deseado debe estar entre 0 y 99.99%.")
@dataclass(frozen=True)
class ValuationResult:
    market_price:float; total_non_purchase_cost:float; maximum_purchase_price:float; recommended_offer:float; expected_profit_at_max:float; expected_profit_at_recommended:float; expected_margin_at_max_percent:float; expected_margin_at_recommended_percent:float; viable:bool; notes:tuple[str,...]=field(default_factory=tuple)
