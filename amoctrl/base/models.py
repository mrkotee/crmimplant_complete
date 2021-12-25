import os
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class PipelineStatuses(Base):
    __tablename__  = "statuses"

    id = Column(Integer, primary_key=True)
    pipeline_id = Column(Integer)
    status_id = Column(Integer, unique=True)
    status_name = Column(String)
    sort_index = Column(Integer)

    def __init__(self, pipeline_id, status_id, status_name, sort_index):
        self.pipeline_id = pipeline_id
        self.status_name = status_name
        self.status_id = status_id
        self.sort_index = sort_index


class AmoStatuses(Base):
    __tablename__ = "amo_statuses"

    id = Column(Integer, primary_key=True)
    amo_id = Column(Integer, unique=True)
    status_id = Column(ForeignKey('statuses.status_id'))

    def __init__(self, amo_id, amo_status_id):
        self.amo_id = amo_id
        self.status_id = amo_status_id


def create_db(basepath):
    if not os.path.exists(basepath):
        engine = create_engine(f"sqlite:///{basepath}")
        Base.metadata.create_all(bind=engine)


def create_session(basepath):
    engine = create_engine(f"sqlite:///{basepath}")
    return sessionmaker(engine)()
