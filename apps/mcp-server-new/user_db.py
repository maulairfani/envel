from __future__ import annotations

from pathlib import Path

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from master_db import make_engine
from models import Base, Note


def init_user_db(user_db_path: Path) -> tuple[Engine, sessionmaker[Session]]:
    engine = make_engine(user_db_path)
    Base.metadata.create_all(engine, tables=[Note.__table__])
    return engine, sessionmaker(bind=engine, future=True)
