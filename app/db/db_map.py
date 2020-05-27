from sqlalchemy import update, delete
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
engine = create_engine(DB)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    last_use = Column(DateTime)
    queries = relationship("Query", back_populates="user")
    settings = relationship("UserSettings", uselist=False, back_populates="user")

    def __init__(self, telegram_id, last_use):
        self.telegram_id = telegram_id
        self.last_use = last_use

    def __repr__(self):
        return f"<User({self.telegram_id}, {self.last_use})>"

    @classmethod
    def insert_user(cls, telegram_id):
        session = Session(bind=engine)
        user = User(telegram_id, datetime.now())
        session.add(user)
        session.commit()
        session.refresh(user)

        session = Session(bind=engine)
        query = Query(user.id)
        session.add(query)
        session.commit()
        session.refresh(query)

        session.add(UserSettings(user.id, editing_query=query.id))
        session.commit()
        session.close()

        session = Session(bind=engine)
        print(session.query(User).all())
        print(session.query(Query).all())
        print(session.query(UserSettings).all())

    @classmethod
    def get_users(cls):
        session = Session(bind=engine)
        return session.query(User).all()

    @classmethod
    def is_user(cls, telegram_id):
        session = Session(bind=engine)
        result = session.query(User).filter(User.telegram_id == telegram_id).all()
        return True if result else False


class Query(Base):
    __tablename__ = 'queries'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    region = Column(String)
    deal = Column(ARRAY(Integer))
    rooms = Column(ARRAY(Integer))
    apartment_type = Column(String)
    price = Column(ARRAY(Float))
    user = relationship('User', back_populates='queries', uselist=False)

    def __init__(self, user_id, region=None, deal=None, rooms=None, apartment_type=None, price=None):
        self.user_id = user_id
        self.region = region
        self.deal = deal
        self.rooms = rooms
        self.apartment_type = apartment_type
        self.price = price

    def __repr__(self):
        return f"<Query({self.user_id}, {self.region}, {self.deal}, {self.rooms}, {self.apartment_type}, {self.price})>"


class UserSettings(Base):
    """
    user_id: int
        User.id
    current_edit_msg: int.
        Telegram message id of current message with main search terms.
    editing_query: int
        Queries.id of last user's query.
    """
    __tablename__ = 'user_settings'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    current_edit_msg = Column(Integer)
    editing_query = Column(Integer)
    user = relationship('User', back_populates='settings', uselist=False)

    def __init__(self, user_id, current_edit_msg=None, editing_query=None):
        self.user_id = user_id
        self.current_edit_msg = current_edit_msg
        self.editing_query = editing_query

    def __repr__(self):
        return f"<UserSettings({self.user_id}, {self.current_edit_msg}, {self.editing_query})>"

    @classmethod
    def update_current_edit_msg(cls, telegram_id, message_id):
        session = Session(bind=engine)
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).one()
            user.settings.current_edit_msg = message_id
            session.commit()
        except Exception:
            print(traceback.format_exc())
            session.rollback()
        finally:
            session.close()

    @classmethod
    def get_current_edit_msg(cls, telegram_id):
        session = Session(bind=engine)
        user = session.query(User).filter(User.telegram_id == telegram_id).one()
        return user.settings.current_edit_msg


def insert_to_db(data):
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



