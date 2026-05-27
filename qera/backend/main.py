from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from backend.config import settings
    from backend.database import init_db, close_db
    from backend.middlewares.rate_limit import limiter
    from backend.routers.auth_router import router as auth_router
    from backend.routers.health import router as health_router
    from backend.routers.question_router import router as question_router
    from backend.routers.comment_router import router as comment_router
except ImportError:
    from config import settings
    from database import init_db, close_db
    from middlewares.rate_limit import limiter
    from routers.auth_router import router as auth_router
    from routers.health import router as health_router
    from routers.question_router import router as question_router
    from routers.comment_router import router as comment_router

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI(title="QERA Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

def _rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    await init_db(app)

@app.on_event("shutdown")
async def shutdown_event():
    await close_db(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(question_router)
app.include_router(comment_router)
