from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_HOST = "192.168.105.81"  # ← MySQL VM의 실제 IP 넣기
DB_PORT = "3306"
DB_USER = "hj-db"
DB_PASS = "Hani6967!"
DB_NAME = "projecta1"

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
