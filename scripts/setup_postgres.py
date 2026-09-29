"""Setup script to automatically create UDAAN database and initialize schema."""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


def setup():
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres123")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5435")
    target_db = os.getenv("DB_NAME", "UDAAN")

    print("\n--- Connecting to PostgreSQL container to check database ---")

    # Connect to default 'postgres' database first
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=port
        )
    except Exception as e:
        # If 'postgres' default db is not available, try 'leetcode'
        try:
            conn = psycopg2.connect(
                dbname="leetcode",
                user=user,
                password=password,
                host=host,
                port=port
            )
        except Exception as e2:
            print(f"Error connecting to PostgreSQL on {host}:{port}: {e2}")
            return False

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if target database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (target_db,))
    exists = cur.fetchone()

    if not exists:
        print(f"Database '{target_db}' does not exist yet. Creating database '{target_db}' now...")
        cur.execute(f'CREATE DATABASE "{target_db}";')
        print(f"Database '{target_db}' created successfully!")
    else:
        print(f"Database '{target_db}' already exists!")

    cur.close()
    conn.close()

    # Now run table creation and migration
    print("\n--- Initializing tables and migrating snapshot fares into database ---")
    from storage.db import DatabaseStore
    from storage.snapshot import SnapshotStore

    db = DatabaseStore()
    if not db.is_connected:
        print("Failed to connect to newly created database.")
        return False

    db.create_all_tables()
    snapshot = SnapshotStore()
    fares = snapshot.load()
    if fares:
        db.insert_fares(fares)
        print(f"Successfully migrated {len(fares)} fare observations into PostgreSQL 'fares' table!")

    print("\nSetup complete! You can now run: python -m scripts.inspect_db\n")
    return True


if __name__ == "__main__":
    setup()
