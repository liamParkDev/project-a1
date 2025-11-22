from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ------------ DB CONFIG ----------------
DB_HOST = "192.168.105.81"
DB_PORT = "3306"
DB_USER = "hj-db"
DB_PASS = "Hani6967!"
DB_NAME = "projecta1"

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ------------ ENGINE ----------------
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,    
    pool_recycle=3600,      
    echo=False       
)

# ------------ SESSION ----------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ------------ BASE ----------------
Base = declarative_base()

# ------------ DEPENDENCY ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
