from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
import db.crud as crud

router = APIRouter(prefix="/translate", tags=["Translate"])


@router.post("/queue")
def add_job(text: str, target_lang: str, source_lang: str = "auto", db: Session = Depends(get_db)):
    job = crud.add_translate_job(db, text, source_lang, target_lang)
    return {"status": "queued", "job_id": job.id}
