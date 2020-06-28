from sqlalchemy import create_engine
import traceback

from .models import DB, Base


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
