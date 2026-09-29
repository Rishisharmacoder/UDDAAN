"""Redis + RQ task queue configuration."""
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAMES = ["high", "default", "low"]
