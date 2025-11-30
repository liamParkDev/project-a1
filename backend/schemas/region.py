# schemas/region.py
from pydantic import BaseModel
from typing import Optional


class RegionBase(BaseModel):
    country_code: str = "TW"
    city: str
    district: str
    name: str
    center_lat: float
    center_lng: float
    radius_km: float = 2.0


class RegionCreate(RegionBase):
    pass


class RegionOut(RegionBase):
    id: int

    class Config:
        from_attributes = True


class GPSVerifyRequest(BaseModel):
    region_id: int
    lat: float
    lng: float


class GPSVerifyResponse(BaseModel):
    success: bool
    distance_km: float
    message: str
    region: Optional[RegionOut] = None
