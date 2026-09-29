from api.routers.index import router as index_router
from api.routers.fares import router as fares_router
from api.routers.datasource import router as datasource_router
from api.routers.health import router as health_router

__all__ = ["index_router", "fares_router", "datasource_router", "health_router"]
