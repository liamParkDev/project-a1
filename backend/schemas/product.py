# schemas/product.py
from pydantic import BaseModel
from typing import List, Optional
from db.models import ProductCondition, ProductTradeType, ProductStatus


class ProductImageCreate(BaseModel):
    image_url: str
    sort_order: int = 0


class ProductCreate(BaseModel):
    title: str
    price: int
    description: Optional[str] = None
    category_id: Optional[int] = None
    region_id: int
    condition: ProductCondition = ProductCondition.used
    trade_type: ProductTradeType = ProductTradeType.direct
    lat: Optional[float] = None
    lng: Optional[float] = None
    images: List[ProductImageCreate] = []


class ProductUpdate(BaseModel):
    title: Optional[str]
    price: Optional[int]
    description: Optional[str]
    category_id: Optional[int]
    condition: Optional[ProductCondition]
    trade_type: Optional[ProductTradeType]
    status: Optional[ProductStatus]
    lat: Optional[float]
    lng: Optional[float]


class ProductResponse(BaseModel):
    id: int
    title: str
    price: int
    description: Optional[str]
    status: ProductStatus
    like_count: int
    seller_id: int
    region_id: int

    class Config:
        orm_mode = True


class ProductDetailResponse(ProductResponse):
    images: List[ProductImageCreate]
