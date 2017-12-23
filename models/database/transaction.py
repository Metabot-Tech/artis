from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric
from models.database.status import Status

Base = declarative_base()


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime)
    updated = Column(DateTime)
    profit = Column(Numeric(25, 18))
    status = Column(Enum(Status))
    error = Column(String)

    def __repr__(self):
        return "<Transaction(id='%s', status='%s')>" % (self.id, self.status)
