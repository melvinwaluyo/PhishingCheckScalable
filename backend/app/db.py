# backend/app/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get individual components from environment
user = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
host = os.getenv('POSTGRES_HOST')
port = os.getenv('POSTGRES_PORT')
db_name = os.getenv('POSTGRES_DB')

# --- Fail Fast if Not Set ---
if not all([user, password, host, port, db_name]):
    raise ValueError("FATAL ERROR: One or more PostgreSQL environment variables "
                     "(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, "
                     "POSTGRES_PORT, POSTGRES_DB) are not set.")

# Build the connection string
PG_CONNECTION = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

print(f"Attempting to connect to DB at {host}...")

engine = create_engine(PG_CONNECTION)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()