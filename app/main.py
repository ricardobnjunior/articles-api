"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import router
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Articles API", version="1.0.0")

app.include_router(router)
