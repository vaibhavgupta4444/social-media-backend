from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.connection import engine, Base
from app.routers import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass

app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
# app.include_router(tasks.router)

@app.get("/", tags=["Root"])
def root():
    return {"message": "FastAPI project running"}