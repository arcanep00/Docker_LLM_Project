from app.db.base import base
from app.db.database import engine

import app.models

base.metadata.create_all(
    bind=engine
)

print("Tables Created")