from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from database.models.coins import Coins
from database.models.markets import Markets
from database.models.status import Status
from database.models.transaction import Transaction

Base = declarative_base()


class Move(Base):
    __tablename__ = 'moves'

    id = Column(Integer, primary_key=True)
    transaction = Column(Integer, ForeignKey(Transaction.id)),
    created = Column(DateTime)
    updated = Column(DateTime)
    origin = Column(Enum(Markets))
    destination = Column(Enum(Markets))
    amount = Column(Numeric(25, 18))
    coin = Column(Enum(Coins))
    status = Column(Enum(Status))
    error = Column(String)

    def __repr__(self):
        return "<Move(id='%s', status='%s')>" % (self.id, self.status)
