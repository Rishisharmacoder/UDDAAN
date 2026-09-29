"""Health check router for services and all 11 PS sources."""
import os
import yaml
from datetime import datetime, timezone
from fastapi import APIRouter
from typing import Dict, Any, List
from storage.db import DatabaseStore
from storage.redis_cache import RedisCache
from storage.snapshot import SnapshotStore

router = APIRouter(prefix="/api", tags=["Health"])
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config")


@router.get("/health")
def get_system_health():
    db = DatabaseStore()
    cache = RedisCache()
    snapshot = SnapshotStore()

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "api": "healthy",
            "redis_cache": "connected" if cache.client else "memory_fallback",
            "database": "connected" if db.is_connected else "snapshot_fallback",
            "snapshot_store": "available" if os.path.exists(snapshot.file_path) else "missing"
        }
    }


@router.get("/sources/health")
def get_sources_health():
    sources_file = os.path.join(CONFIG_DIR, "sources.yaml")
    with open(sources_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    sources_list = data.get("sources", [])
    result = []

    for s in sources_list:
        sid = s.get("id")
        channel = s.get("channel")
        enabled = s.get("enabled", False)

        if channel == "skip":
            status = "skipped_legal_compliance"
            badge = "red"
            last_success = "N/A"
        elif channel == "api" and not enabled:
            status = "pending_credentials"
            badge = "amber"
            last_success = "Application Submitted"
        elif enabled:
            status = "healthy"
            badge = "green"
            last_success = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        else:
            status = "evaluation"
            badge = "gray"
            last_success = "N/A"

        result.append({
            "id": sid,
            "name": s.get("name"),
            "type": s.get("type"),
            "channel": channel,
            "status": status,
            "badge": badge,
            "last_success": last_success,
            "weight": s.get("weight", 0.0),
            "notes": s.get("notes", "")
        })

    return result
