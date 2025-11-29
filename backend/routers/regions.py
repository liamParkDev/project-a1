# routers/regions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_user, get_current_admin
from db.crud_region import (
    create_region,
    get_all_regions,
    get_regions_by_city,
    get_region,
    delete_region,
    verify_gps,
)
from schemas.region import RegionCreate, RegionResponse, GPSVerifyRequest

router = APIRouter(prefix="/regions", tags=["Regions"])


# =============================
# 지역 기본 CRUD
# =============================

@router.post("/", response_model=RegionResponse)
def add_region(payload: RegionCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return create_region(db, payload)


@router.get("/", response_model=list[RegionResponse])
def list_regions(db: Session = Depends(get_db)):
    return get_all_regions(db)


@router.get("/city/{city}", response_model=list[RegionResponse])
def list_by_city(city: str, db: Session = Depends(get_db)):
    return get_regions_by_city(db, city)


@router.delete("/{region_id}")
def remove_region(region_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    region = get_region(db, region_id)
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    delete_region(db, region)
    return {"status": "deleted"}


# =============================
# GPS 인증
# =============================

@router.post("/verify-gps")
def gps_verify(payload: GPSVerifyRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    region, error = verify_gps(db, user, payload.lat, payload.lng)

    if error == "NO_REGION":
        raise HTTPException(400, "지역 데이터가 없습니다. 관리자에게 문의하세요.")

    if error == "OUT_OF_RANGE":
        raise HTTPException(400, "현재 위치가 인증 반경을 벗어났습니다.")

    return {
        "status": "verified",
        "region_id": region.id,
        "region_name": f"{region.city} {region.district} {region.name}"
    }
