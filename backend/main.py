from fastapi import FastAPI
from db.session import Base, engine
from routers import items, users, auth

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(items.router)

@app.get("/")
def root():
    return {"message": "API Running!"}

@app.get("/db-test")
def db_test():
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return {"status": "ok", "message": "DB connected!"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}