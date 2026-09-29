"""RQ worker process runner."""
import os
import time
from loguru import logger

try:
    import redis
    from rq import Worker, Queue, Connection
except ImportError:
    redis = None
    Worker = None


def run_worker():
    if not Worker or not redis:
        logger.warning("[RQ WORKER] RQ or Redis library not available; worker operating in standby.")
        while True:
            time.sleep(10)

    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    try:
        conn = redis.from_url(redis_url)
        with Connection(conn):
            worker = Worker(["default", "high", "low"])
            logger.info(f"[RQ WORKER] Listening for tasks on {redis_url}...")
            worker.work()
    except Exception as e:
        logger.error(f"[RQ WORKER] Failed to start: {e}. Retrying in 10s...")
        time.sleep(10)


if __name__ == "__main__":
    run_worker()
