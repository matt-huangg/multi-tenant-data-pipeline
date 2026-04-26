"""Small smoke test for the database connection."""

from sqlalchemy import text

from app.db.session import SessionLocal


def test_connection():
    """Run a trivial query to confirm the database is reachable."""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        print(result.scalar_one())
    finally:
        db.close()


if __name__ == "__main__":
    test_connection()
