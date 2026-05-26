from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PriceHistoryOut(BaseModel):
    id: str
    product_id: str
    price: Optional[float]
    currency: str
    availability: bool
    collected_at: datetime

    class Config:
        from_attributes = True