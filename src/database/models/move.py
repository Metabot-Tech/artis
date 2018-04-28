from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .coins import Coins
from .markets import Markets
from .status import Status
from .base import Base


class Move(Base):
    __tablename__ = 'moves'

    id = Column(Integer, primary_key=True)
    #transaction_id = Column(Integer, ForeignKey(Transaction.id))
    #transaction = relationship(Transaction, backref='moves')
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
