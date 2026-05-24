from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base, User


def make_engine(db_path: Path) -> Engine:
    return create_engine(
        f"sqlite:///{db_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )


def init_master_db(data_dir: Path, master_db_path: Path) -> tuple[Engine, sessionmaker[Session]]:
    data_dir.mkdir(parents=True, exist_ok=True)
    engine = make_engine(master_db_path)
    Base.metadata.create_all(engine, tables=[User.__table__])
    return engine, sessionmaker(bind=engine, future=True)
