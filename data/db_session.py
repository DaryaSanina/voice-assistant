import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
import sqlalchemy.ext.declarative as dec

SqlAlchemyBase = dec.declarative_base()  # Create a model base

__factory = None


def global_init(db_file: str):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():  # The database filename is empty
        raise Exception("You need to specify the database file")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    engine = sa.create_engine(conn_str, echo=False)  # Create an engine
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models  # Import all models

    SqlAlchemyBase.metadata.create_all(engine)  # Add all models to the database


def create_session() -> Session:
    global __factory
    return __factory()
