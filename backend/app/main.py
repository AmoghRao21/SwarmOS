from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api import routes  

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting SwarmOS...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan, title="SwarmOS Brain")


app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "SwarmOS Online 🟢"}