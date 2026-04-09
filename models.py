# from sqlalchemy import Column, String, Integer, Float
# from db import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True)
#     phone = Column(String)
#     token = Column(String)

# class Mandate(Base):
#     __tablename__ = "mandates"

#     id = Column(String, primary_key=True)
#     user_id = Column(String)
#     amount = Column(Float)
#     status = Column(String)
#     payment_order_id = Column(String)
#     checkout_url = Column(String)

from sqlalchemy import Column, Integer, String, JSON, Numeric
from Database import engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Mandate(Base):
    __tablename__ = "mandates"

    id = Column(Integer, primary_key=True)
    mandate_id = Column(String, unique=True)
    webhook_status = Column(String)
    real_state = Column(String)
    full_payload = Column(JSON)


class Installment(Base):
    __tablename__ = "installments"

    id = Column(Integer, primary_key=True)
    installment_id = Column(String, unique=True)
    mandate_id = Column(String)
    status = Column(String)
    amount = Column(Numeric)
    full_payload = Column(JSON)


Base.metadata.create_all(bind=engine)