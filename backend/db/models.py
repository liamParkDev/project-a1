from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db.session import SessionLocal, engine, Base

app = FastAPI()

# 테스트용 DB 연결 확인 API
@app.get("/db-test")
def db_test():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return {"status": "ok", "message": "DB connected!"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
