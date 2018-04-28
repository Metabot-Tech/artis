import datetime
from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric
from .status import Status
from .base import Base


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    status = Column(Enum(Status), default=Status.DONE)
    error = Column(String)

    def __repr__(self):
        return "<Transaction(id='%s', status='%s')>" % (self.id, self.status)
