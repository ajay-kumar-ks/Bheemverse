from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.config import settings
    from backend.database import init_db, close_db
    from backend.routers.health import router as health_router
except ImportError:
    from config import settings
    from database import init_db, close_db
    from routers.health import router as health_router

app = FastAPI(title="QERA Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db(app)

@app.on_event("shutdown")
async def shutdown_event():
    await close_db(app)

app.include_router(health_router)
