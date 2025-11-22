from fastapi import FastAPI , Depends
from sqlalchemy import text
from db.session import SessionLocal
from routers import users, products, translate

app = FastAPI(title="Project A1 API")

app.include_router(users.router)
app.include_router(products.router)
app.include_router(translate.router)

@app.get("/")
def root():
    return {"message": "Hello from FastAPI backend!"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}

@app.get("/db-test")
def db_test(db = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "DB connected!"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

