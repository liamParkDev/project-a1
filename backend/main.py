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
