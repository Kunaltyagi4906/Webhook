# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/rocketpay"

# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(bind=engine)

# Base = declarative_base()



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/rocketpay_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)