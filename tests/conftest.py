import os
import tempfile

# Configure environment BEFORE importing the application, because
# app.db.database creates the engine at import time from DATABASE_URL.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("UPLOAD_DIR", tempfile.mkdtemp(prefix="uploads_test_"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import base
import app.models  # noqa: F401  (register models on base.metadata)
from app.db.dependency import get_db
from app.api import job_routers
from app.main import app


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    base.metadata.create_all(eng)
    try:
        yield eng
    finally:
        base.metadata.drop_all(eng)


@pytest.fixture
def session_factory(engine):
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


@pytest.fixture
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(session_factory, monkeypatch):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Avoid dispatching to a real Celery/Redis broker during tests.
    monkeypatch.setattr(
        job_routers.process_csv_job,
        "delay",
        lambda *args, **kwargs: None,
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
