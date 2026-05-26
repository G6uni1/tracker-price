from pydantic import BaseModel, HttpUrl
from typing import Optional

class ProductCreate(BaseModel):
    url: str
    store: str
    target_price: Optional[float] = None

class ProductOut(BaseModel):
    id: str
    user_id: str
    url: str
    store: str
    product_name: Optional[str]
    target_price: Optional[float]
    is_active: bool
    created_at: str

    class Config:
        from_attributes = True