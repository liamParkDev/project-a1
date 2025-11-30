# db/crud_region.py
from typing import List, Optional
from sqlalchemy.orm import Session

from db import models
from schemas.region import RegionCreate


def create_region(db: Session, data: RegionCreate) -> models.Region:
    region = models.Region(
        country_code=data.country_code,
        city=data.city,
        district=data.district,
        name=data.name,
        center_lat=data.center_lat,
        center_lng=data.center_lng,
        radius_km=data.radius_km,
    )
    db.add(region)
    db.commit()
    db.refresh(region)
    return region


def get_region(db: Session, region_id: int) -> Optional[models.Region]:
    return db.query(models.Region).filter(models.Region.id == region_id).first()


def list_regions(
    db: Session,
    city: Optional[str] = None,
    district: Optional[str] = None,
) -> List[models.Region]:
    q = db.query(models.Region)

    if city:
        q = q.filter(models.Region.city == city)
    if district:
        q = q.filter(models.Region.district == district)

    return q.order_by(
        models.Region.city,
        models.Region.district,
        models.Region.name,
    ).all()
