from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
# Import models so the database knows they exist
from app.models import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting SwarmOS Brain...")
    # This creates the tables in the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Tables Created!")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "SwarmOS Database Connected 🔗"}