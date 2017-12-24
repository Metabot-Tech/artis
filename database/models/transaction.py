from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from database.models.status import Status
import datetime

Base = declarative_base()


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    profit = Column(Numeric(25, 18), default=0)
    status = Column(Enum(Status), default=Status.CREATED)
    error = Column(String)

    def __repr__(self):
        return "<Transaction(id='%s', status='%s')>" % (self.id, self.status)
