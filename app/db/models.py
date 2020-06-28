from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

from datetime import datetime
import math
from random import randint
import traceback

from app.configs.db import RANDOM_HOME_DB_USER, RANDOM_HOME_DB_PASSWORD, DB_SERVER_IP
from app.tools import CianApiParser, proxy_processor


DB = 'postgresql+psycopg2://{}:{}@{}/random_home'.format(RANDOM_HOME_DB_USER,
                                                         RANDOM_HOME_DB_PASSWORD,
                                                         DB_SERVER_IP)

Base = declarative_base()
engine = create_engine(DB)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    registration_date = Column(DateTime)
    queries = relationship("Query", back_populates="user")
    settings = relationship("UserSettings", uselist=False, back_populates="user")
    tasks = relationship("Task", back_populates="user")

    def __init__(self, telegram_id, first_name, last_name, registration_date):
        self.telegram_id = telegram_id
        self.first_name = first_name
        self.last_name = last_name
        self.registration_date = registration_date

    def __repr__(self):
        return f"<User({self.telegram_id}, {self.first_name}, {self.last_name}, {self.registration_date})>"

    @classmethod
    def insert_user(cls, telegram_id, first_name, last_name):
        session = Session(bind=engine)
        user = User(telegram_id, first_name, last_name, datetime.now())
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
    pages = Column(Integer)
    region = Column(ARRAY(Integer))
    deal = Column(String)
    underground = Column(Integer)
    rooms = Column(ARRAY(Integer))
    apartment_type = Column(Integer)
    price = Column(ARRAY(Float))
    user = relationship('User', back_populates='queries', uselist=False)
    tasks = relationship('Task', back_populates='query')

    def __init__(self, user_id, pages=None, region=None, deal=None, underground=None, rooms=None,
                 apartment_type=None, price=None):
        self.user_id = user_id
        self.pages = pages
        self.region = region
        self.deal = deal
        self.underground = underground
        self.rooms = rooms
        self.apartment_type = apartment_type
        self.price = price

    def __repr__(self):
        return f"<Query({self.user_id}, {self.pages}, {self.region}, {self.deal}, {self.underground}" \
               f" {self.rooms}, {self.apartment_type}, {self.price})>"

    async def process_query(self, session=None):
        if not session:
            session = Session(bind=engine)

        page = randint(1, self.pages) if self.pages else 1

        constructor = CianApiParser.parser.QueryConstructor(page=page,
                                                            region=self.region,
                                                            type=self.deal,
                                                            underground_id=self.underground,
                                                            room=self.rooms,
                                                            building_status=self.apartment_type,
                                                            price=self.price)

        flats_in_storage = session.query(Flat).filter(Flat.query_id == self.id).all()
        api_manager = CianApiParser.parser.ApiManager(query=constructor, flats_in_storage=flats_in_storage)

        flat, attempts = None, 1
        while not flat and attempts <= 3:
            print('attempt: ', attempts)
            flat = await api_manager.run()
            attempts += 1

        if not flat:
            raise NotNewFlats

        flat_obj = Flat(query_id=self.id,
                        url=flat.url,
                        cian_id=flat.cian_id,
                        price=flat.price,
                        coordinates=[flat.coordinates['lat'], flat.coordinates['lng']],
                        city=flat.address['city'],
                        street=flat.address['street'],
                        house=flat.address['house'],
                        object_type=flat.info['object_type'],
                        floor=flat.info['floor'],
                        area=flat.info['area'],
                        phone=flat.phone,
                        description=flat.description
                 )
        session.add(flat_obj)
        session.commit()
        session.refresh(flat_obj)

        session.add(
            FlatUnderground(
                flat_id=flat_obj.id,
                cian_flat_id=flat.cian_id,
                name=flat.underground['name'],
                time=flat.underground['time'],
                timeunits=flat.underground['units'],
                type=flat.underground['type']
            )
        )

        pages_count = math.ceil(api_manager.data['offersCount'] / 28)
        session.query(Query).\
            filter(Query.id == self.id).\
            update({'pages': pages_count if pages_count <= 54 else 54})
        session.commit()
        return flat

    def check_repeated_flat(self, session):
        pass


class NotNewFlats(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "Couldn't find new flats."


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


class Flat(Base):
    __tablename__ = "flats"
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('queries.id'))
    url = Column(String)
    cian_id = Column(Integer)
    price = Column(Integer)
    coordinates = Column(ARRAY(Float))
    city = Column(String)
    street = Column(String)
    house = Column(String)
    object_type = Column(String)
    floor = Column(String)
    area = Column(String)
    phone = Column(String)
    description = Column(String)
    undergrounds = relationship('FlatUnderground', back_populates='flat')

    def __init__(self, query_id: int, url: str, cian_id: int, price: int,
                 coordinates: list, city: str, street: str = None, house: str = None,
                 object_type: str = None, floor: str = None, area: str = None,
                 phone: str = None, description :str = None):
        self.query_id = query_id
        self.url = url
        self.cian_id = cian_id
        self.price = price
        self.coordinates = coordinates
        self.city = city
        self.street = street
        self.house = house
        self.object_type = object_type
        self.floor = floor
        self.area = area
        self.phone = phone
        self.description = description

    def __repr__(self):
        return "Flat " + ", ".join(self.__dict__.items())


class FlatUnderground(Base):
    __tablename__ = "flat_underground"
    id = Column(Integer, primary_key=True)
    flat_id = Column(Integer, ForeignKey('flats.id'))
    cian_flat_id = Column(Integer)
    name = Column(String)
    time = Column(Integer)
    timeunits = Column(String)
    type = Column(String)
    flat = relationship('Flat', back_populates='undergrounds', uselist=False)

    def __init__(self, flat_id, cian_flat_id, name, time, timeunits, type):
        self.flat_id = flat_id
        self.cian_flat_id = cian_flat_id
        self.name = name
        self.time = time
        self.timeunits = timeunits
        self.type = type

    def __repr__(self):
        return f"FlatUnderground ({self.id}, {self.flat_id}, {self.cian_flat_id}, {self.name}, " \
               f"{self.time}, {self.timeunits}, {self.type})"


class ProxyList(Base):
    __tablename__ = "proxy_list"
    id = Column(Integer, primary_key=True)
    address = Column(String)
    available = Column(Boolean)

    def __init__(self, address: str, available: bool = True):
        self.address = address
        self.available = available

    def __repr__(self):
        return f"<ProxyList({self.address}, {self.available})>"

    @classmethod
    def update_table(cls):
        session = Session(bind=engine)
        session.query(ProxyList).filter(ProxyList.available == False).delete()
        safe_commit(session)

        old_proxies = set([proxy.address for proxy in session.query(ProxyList).all()])
        new_proxies = proxy_processor.get_proxies_from_source_txt()
        proxy_objects = [ProxyList(proxy) for proxy in new_proxies if proxy not in old_proxies]

        session = Session(bind=engine)
        session.bulk_save_objects(proxy_objects)
        safe_commit(session)

    def remember_invalid_proxy(self):
        session = Session(bind=engine)
        self.available = False
        safe_commit(session)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    query_id = Column(Integer, ForeignKey('queries.id'))
    task_type = Column(Integer)
    execution_hour = Column(Integer)
    day_of_last_execution = Column(Integer)
    user = relationship('User', back_populates='tasks', uselist=False)
    query = relationship('Query', back_populates='tasks', uselist=False)

    def __init__(self, user_id, task_type, query_id, execution_hour, day_of_last_execution=0):
        self.user_id = user_id
        self.task_type = task_type
        self.execution_hour = execution_hour
        self.day_of_last_execution = day_of_last_execution
        self.query_id = query_id

    def __repr__(self):
        return f"Task({self.user_id}, {self.task_type}, {self.execution_hour}, {self.day_of_last_execution}, " \
               f"{self.query_id})"

    @property
    def task_func(self):
        tasks = {
            1: self.send_random_flat
        }
        return tasks[self.task_type]

    async def send_random_flat(self):
        flat = await self.query.process_query()
        if flat:
            return flat
        else:
            print(f"{self} failed")
            return None

    def execute_task(self):
        return self.task_func()


def safe_commit(session):
    try:
        session.commit()
    except Exception:
        print(traceback.format_exc())
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    pass
