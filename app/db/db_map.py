from sqlalchemy import Table
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

from datetime import datetime
import traceback

from app.configs.db import RANDOM_HOME_DB_USER, RANDOM_HOME_DB_PASSWORD, DB_SERVER_IP

DB = 'postgresql+psycopg2://{}:{}@{}/random_home_test'.format(RANDOM_HOME_DB_USER,
                                                              RANDOM_HOME_DB_PASSWORD,
                                                              DB_SERVER_IP)  #TODO test db
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String)
    last_use = Column(DateTime)
    query = relationship("Query")

    def __init__(self, telegram_id, last_use):
        self.telegram_id = telegram_id
        self.last_use = last_use

    def __repr__(self):
        return "<User({self.telegram_id}, {self.last_use})>"

    @classmethod
    def add_user(cls, engine, telegram_id):
        add_to_database(engine, User(telegram_id, datetime.now()))

    @classmethod
    def get_users(cls, engine):
        session = Session(bind=engine)
        return session.query(User).all()

    @classmethod
    def is_user(cls, engine, telegram_id):
        session = Session(bind=engine)
        result = session.query(User.telegram_id == telegram_id)
        if result:
            return True
        else:
            return False


class Query(Base):
    __tablename__ = 'queries'
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey('users.id'))
    region = Column(String)
    deal = Column(ARRAY(Integer))
    rooms = Column(ARRAY(Integer))
    apartment_type = Column(String)
    price = Column(ARRAY(Float))

    def __init__(self, user, region, deal, rooms, apartment_type, price):
        self.user = user
        self.region = region
        self.deal = deal
        self.rooms = rooms
        self.apartment_type = apartment_type
        self.price = price

    def __repr__(self):
        return "<Query({self.user}, {self.region}, {self.deal}, {self.rooms}, {self.apartment_type}, {self.price})>"

    @classmethod
    def add_query_for_user(cls, engine, user, region, deal, rooms, apartment_type, price):
        add_to_database(engine, Query(user, region, deal, rooms, apartment_type, price))


def add_to_database(engine, data):
    session = Session(bind=engine)
    try:
        session.add(data)
        session.commit()
    except Exception:
        print(traceback.format_exc())
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    link1 = 'postgresql+psycopg2://{RANDOM_HOME_DB_USER}:{RANDOM_HOME_DB_PASSWORD}@127.0.0.1:5432/random_home_db'
    test_db = create_engine(link1)
    Base.metadata.create_all(test_db)



