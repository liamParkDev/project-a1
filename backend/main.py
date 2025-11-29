from fastapi import FastAPI, Depends
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

from db.session import get_db, engine
from db.session import Base
from routers import users, products, translate


app = FastAPI(title="Project A1 API")

# ==============================
# DB 테이블 자동 생성 (startup)
# ==============================
@app.on_event("startup")
def on_startup():
    print(">> Creating database tables if not exist...")
    Base.metadata.create_all(bind=engine)
    print(">> DB table check complete.")


# ==============================
# ROUTERS
# ==============================
app.include_router(users.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(translate.router, prefix="/api")


# ==============================
# CORS
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.local", "http://app.local"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================
# BASIC ROUTES
# ==============================
@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}


@app.get("/api/db-test")
def db_test(db=Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "DB connected!"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
