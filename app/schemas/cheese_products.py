from pydantic import BaseModel
from datetime import date
from typing import Optional, List

class CheeseProducts(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    each_price: Optional[float] = None
    case_price: Optional[float] = None
    sku_code: Optional[str] = None
    upc_code: Optional[str] = None
    each_size: Optional[str] = None
    case_size: Optional[str] = None
    each_weight: Optional[float] = None
    case_weight: Optional[float] = None
    weight_unit: Optional[str] = 'LB'
    each_quantity: Optional[int] = None
    case_quantity: Optional[int] = None
    url: Optional[str] = None
    sample_image: Optional[str] = None
    other_images: Optional[List[str]] = None
    related_products: Optional[List[str]] = None
    stock: Optional[str] = None
    alert: Optional[str] = None
    special: Optional[str] = None

    class Config:
        from_attributes = True