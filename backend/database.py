import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_URL = f"sqlite:///{BASE_DIR / 'genie_log.db'}"
DATA_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

engine_kwargs = {}
if DATA_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATA_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
