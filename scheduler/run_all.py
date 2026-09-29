"""APScheduler 24x7 runner daemon."""
import time
import signal
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger
import scrapers  # ensure all adapters registered
from scheduler.jobs import sweep_morning, sweep_evening, compute_index_job, health_ping_job


def start_scheduler():
    logger.info("[SCHEDULER DAEMON] Initializing APScheduler with 24x7 jobs...")
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

    # 1. Sweep-A: Morning 06:00 IST
    scheduler.add_job(sweep_morning, "cron", hour=6, minute=0, id="sweep_morning")

    # 2. Sweep-B: Evening 18:00 IST
    scheduler.add_job(sweep_evening, "cron", hour=18, minute=0, id="sweep_evening")

    # 3. Nightly APIx Index: 21:00 IST
    scheduler.add_job(compute_index_job, "cron", hour=21, minute=0, id="compute_index")

    # 4. Health ping: every 30 minutes
    scheduler.add_job(health_ping_job, "interval", minutes=30, id="health_ping")

    scheduler.start()
    logger.info("[SCHEDULER DAEMON] APScheduler started successfully. Active jobs:")
    for job in scheduler.get_jobs():
        logger.info(f"  * [{job.id}] Next run: {job.next_run_time}")

    def shutdown_handler(sig, frame):
        logger.info("[SCHEDULER DAEMON] Shutting down gracefully...")
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    try:
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    start_scheduler()
