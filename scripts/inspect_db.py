"""Utility script to inspect PostgreSQL database connection and view table data."""
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
from storage.db import DatabaseStore

try:
    from sqlalchemy import text
except ImportError:
    text = None


def inspect_database():
    print("\n" + "=" * 60)
    print("   APIx DATABASE CONNECTION & DATA INSPECTOR")
    print("=" * 60 + "\n")

    db = DatabaseStore()

    if not db.is_connected:
        print("[STATUS] [OFFLINE] Database NOT Connected")
        print(f"  Attempted URI : {os.getenv('DATABASE_URL', 'Not Set')}")
        print("  Reason        : PostgreSQL server is not running or port 5435 is closed.")
        print("  Fallback      : APIx is automatically reading from data/snapshot.csv.\n")
        print("Tip to connect your Docker container:")
        print("  1. Make sure Docker container is running: docker ps")
        print("  2. To load data into DB when connected: python -m scripts.migrate_csv_to_db\n")
        return

    print("[STATUS] [CONNECTED] Database Connected Successfully to PostgreSQL!")
    print(f"  Host: {db.host} | Port: {db.port} | Database: {db.name} | User: {db.user}\n")

    try:
        with db.engine.connect() as conn:
            # 1. Check Fares Table Count
            res = conn.execute(text("SELECT count(*) FROM fares;"))
            fares_count = res.scalar()
            print(f"  * Table 'fares' Total Rows : {fares_count}")

            # 2. Check Index Values Table Count
            res = conn.execute(text("SELECT count(*) FROM index_values;"))
            index_count = res.scalar()
            print(f"  * Table 'index_values' Rows : {index_count}")

            # 3. Check Sources Table Count
            res = conn.execute(text("SELECT count(*) FROM sources;"))
            sources_count = res.scalar()
            print(f"  * Table 'sources' Rows      : {sources_count}\n")

            # 4. Display Latest 5 Fares
            if fares_count > 0:
                print("  --- Latest 5 Fares Ingested in Database ---")
                rows = conn.execute(text("""
                    SELECT route, "window", price_inr, quality_flag, scraped_at 
                    FROM fares 
                    ORDER BY scraped_at DESC 
                    LIMIT 5;
                """)).fetchall()

                print(f"  {'ROUTE':<10} | {'WINDOW':<8} | {'PRICE (INR)':<12} | {'QUALITY':<8} | {'SCRAPED AT'}")
                print("  " + "-" * 55)
                for r in rows:
                    print(f"  {r[0]:<10} | {r[1]:<8} | INR {float(r[2]):<8,.2f} | {r[3]:<8} | {str(r[4])[:19]}")
                print()
            else:
                print("  Table 'fares' is currently empty.")
                print("  To load snapshot into DB, run: python -m scripts.migrate_csv_to_db\n")

    except Exception as e:
        print(f"Error querying database tables: {e}\n")


if __name__ == "__main__":
    inspect_database()
