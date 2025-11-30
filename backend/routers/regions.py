# routers/regions.py
from datetime import datetime
import math
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from db import models
from db.models import User
from db.models import UserRole  # 이미 models.py에 있음
from schemas.region import RegionCreate, RegionOut, GPSVerifyRequest, GPSVerifyResponse
from core.security import get_current_user, get_current_admin

import db.crud_region as crud_region

router = APIRouter(
    prefix="/regions",
    tags=["Regions"],
)

# -----------------------
# 유틸: 거리 계산 (Haversine)
# -----------------------

def calc_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    위/경도 사이의 거리를 km 단위로 계산 (Haversine formula)
    """
    R = 6371.0  # 지구 반지름 (km)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# -----------------------
# Region CRUD
# -----------------------

@router.get("/", response_model=List[RegionOut])
def list_regions(
    city: Optional[str] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    지역 목록 조회
    - /api/regions
    - /api/regions?city=Taipei
    - /api/regions?city=Taipei&district=中山區
    """
    regions = crud_region.list_regions(db, city=city, district=district)
    return regions


@router.get("/{region_id}", response_model=RegionOut)
def get_region(region_id: int, db: Session = Depends(get_db)):
    region = crud_region.get_region(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region


@router.post("/", response_model=RegionOut)
def create_region_endpoint(
    data: RegionCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """
    Admin 전용 Region 생성 API
    """
    region = crud_region.create_region(db, data)
    return region


# -----------------------
# GPS 인증 API
# -----------------------

@router.post("/verify-gps", response_model=GPSVerifyResponse)
def verify_gps(
    payload: GPSVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    region = crud_region.get_region(db, payload.region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    distance_km = calc_distance_km(
        payload.lat,
        payload.lng,
        region.center_lat,
        region.center_lng,
    )

    if distance_km > region.radius_km:
        return GPSVerifyResponse(
            success=False,
            distance_km=round(distance_km, 3),
            message="선택한 동네 반경 밖에 있습니다.",
            region=None,
        )

    # Update
    current_user.home_region_id = region.id
    current_user.home_lat = payload.lat
    current_user.home_lng = payload.lng
    current_user.gps_verified_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return GPSVerifyResponse(
        success=True,
        distance_km=round(distance_km, 3),
        message="동네 인증이 완료되었습니다.",
        region=RegionOut.model_validate(region),
    )
