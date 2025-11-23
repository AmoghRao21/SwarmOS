from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.api import routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting SwarmOS Brain...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database Tables Created!")
    except Exception as e:
        print(f"⚠️ Database Warning: {e}")
    yield

app = FastAPI(lifespan=lifespan, title="SwarmOS Brain")

# --- THE NUCLEAR CORS FIX ---
app.add_middleware(
    CORSMiddleware,
    # This regex allows http://localhost:3000, http://127.0.0.1:3000, etc.
    allow_origin_regex="http://.*", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the routes
app.include_router(routes.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "SwarmOS Online 🟢"}