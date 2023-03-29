from sqlalchemy import create_engine, Column, BigInteger, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DB_NAME')
port = os.getenv('PORT')

ENGINE = create_engine(os.environ.get("DATABASE_URL").replace("postgres", "postgresql"))

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    subscribed = Column(Boolean, nullable=False, default=True)
    notification_time = Column(Integer, nullable=True, default=9)


class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)


Base.metadata.create_all(ENGINE)
print('Database Successfully created')