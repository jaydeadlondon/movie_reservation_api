import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.utils import get_password_hash


def create_database_if_not_exists():
    if not database_exists(engine.url):
        print(f"Creating database: {engine.url.database}")
        create_database(engine.url)
        print("✅ Database created")
    else:
        print(f"✅ Database already exists: {engine.url.database}")


def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")


def create_initial_admin():
    db = SessionLocal()

    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin:
            print("⚠️  Admin already exists")
            return

        admin = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
        )

        db.add(admin)
        db.commit()

        print("✅ Admin created!")
        print(f"   Username: admin")
        print(f"   Password: admin123")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_database_if_not_exists()
    create_tables()
    create_initial_admin()
