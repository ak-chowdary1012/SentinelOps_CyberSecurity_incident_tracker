from app.database import Base, engine
from app.main import seed_demo_data


if __name__ == "__main__":
    print("Creating database schema...")
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
    print("Database initialized with demo SOC data.")
