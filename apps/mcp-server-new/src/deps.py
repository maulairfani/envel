from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from fastmcp.server.dependencies import get_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


@dataclass
class CurrentUser:
    username: str
    db_path: Path


def current_user() -> CurrentUser:
    token = get_access_token()
    return CurrentUser(
        username=token.claims["sub"],
        db_path=Path(token.claims["db_path"]),
    )


@contextmanager
def user_session(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{db_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)
    try:
        with Session() as session:
            yield session
    finally:
        engine.dispose()
