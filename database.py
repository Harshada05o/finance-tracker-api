from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connection string format: postgresql://username:password@host:port/database_name
DATABASE_URL = "postgresql://postgres:mypassword123@localhost:5432/finance_tracker"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()