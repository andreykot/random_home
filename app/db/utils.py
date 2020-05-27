from sqlalchemy import Table
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
import traceback

from app.db.db_map import DB, Base, User, Query


def get_engine():
    return create_engine(DB)


def send_sql_query(query: str, get_result: bool):
    pass


def safe_commit(session):
    try:
        session.commit()
    except Exception:
        print(traceback.format_exc())
        session.rollback()
    finally:
        session.close()


def init_db():
    engine = create_engine(DB)
    Base.metadata.create_all(engine)


def drop_db():
    pass


if __name__ == '__main__':
    init_db()
