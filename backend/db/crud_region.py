from sqlalchemy.orm import Session
from db.models import Region, User
from schemas.region import RegionCreate
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

def calc_distance_km(lat1, lng1, lat2, lng2):
    R = 6371
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = sin(d_lat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def create_region(db: Session, payload: RegionCreate):
    region = Region(**payload.dict())
    db.add(region)
    db.commit()
    db.refresh(region)
    return region

def get_all_regions(db: Session):
    return db.query(Region).all()

def get_regions_by_city(db: Session, city: str):
    return db.query(Region).filter(Region.city == city).all()

def get_region(db: Session, region_id: int):
    return db.query(Region).filter(Region.id == region_id).first()

def delete_region(db: Session, region: Region):
    db.delete(region)
    db.commit()

def verify_gps(db: Session, user: User, lat: float, lng: float):
    regions = db.query(Region).all()
    if not regions:
        return None, "NO_REGION"

    for region in regions:
        dist = calc_distance_km(lat, lng, region.center_lat, region.center_lng)
        if dist <= region.radius_km:
            user.home_region_id = region.id
            user.gps_verified_at = datetime.utcnow()
            user.home_lat = lat
            user.home_lng = lng
            db.commit()
            db.refresh(user)
            return region, None

    return None, "OUT_OF_RANGE"
