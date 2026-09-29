"""FastAPI Application Main Entrypoint."""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.routers import index_router, fares_router, datasource_router, health_router
from storage.snapshot import SnapshotStore
from index_engine.apix import APIxIndexEngine
from storage.redis_cache import RedisCache

app = FastAPI(
    title="APIx — Real-time Airfare Price Index for India",
    description="MoSPI DIID Automated Airfare Intelligence & CPI Augmentation Platform (SIH26056)",
    version="1.0.0"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(index_router)
app.include_router(fares_router)
app.include_router(datasource_router)
app.include_router(health_router)

# Mount Frontend Static Assets
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard", "static")

if os.path.exists(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="react-assets")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serves the interactive React Dashboard (or static fallback)."""
    react_index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(react_index):
        return FileResponse(react_index)

    dashboard_file = os.path.join(STATIC_DIR, "dashboard.html")
    if os.path.exists(dashboard_file):
        return FileResponse(dashboard_file)
    return {"message": "APIx Platform Online. Visit /docs for Swagger interactive API documentation."}


@app.on_event("startup")
def startup_event():
    logger.info("[APIx STARTUP] Initializing APIx service...")
    store = SnapshotStore()
    df = store.get_dataframe()
    if os.getenv("AUTO_SEED", "false").lower() == "true" and df.empty:
        logger.info("[APIx STARTUP] Seeding initial baseline airfare data...")
        from scripts.seed_data import generate_seed_data
        generate_seed_data()
        df = store.get_dataframe()

    # Warm index cache
    cache = RedisCache()
    if not cache.get_latest_index("monthly"):
        engine = APIxIndexEngine(base_month="2026-07")
        monthly = engine.compute_monthly_series(df)
        cache.set_latest_index("monthly", monthly)
        daily = engine.compute_daily_series(df)
        cache.set_latest_index("daily", daily)
        logger.info("[APIx STARTUP] Index cache initialized.")
