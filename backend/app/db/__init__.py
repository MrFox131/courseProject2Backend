from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..config import db_url
from sqlalchemy.orm import Session

print(db_url)

engine = create_engine(db_url, pool_size=30)

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
