# schemas/region.py
from pydantic import BaseModel
from typing import Optional

class RegionCreate(BaseModel):
    country_code: str = "TW"
    city: str
    district: str
    name: str
    center_lat: float
    center_lng: float
    radius_km: float = 2.0


class RegionResponse(BaseModel):
    id: int
    city: str
    district: str
    name: str
    center_lat: float
    center_lng: float
    radius_km: float

    class Config:
        orm_mode = True


class GPSVerifyRequest(BaseModel):
    lat: float
    lng: float
