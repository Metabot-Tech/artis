import datetime
from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from .coins import Coins
from .markets import Markets
from .status import Status
from .types import Types
from .base import Base


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship("Transaction", backref="trades")
    order_id = Column(Integer)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    market = Column(Enum(Markets))
    type = Column(Enum(Types))
    coin = Column(Enum(Coins))
    amount = Column(Numeric(25, 18))
    price = Column(Numeric(25, 18))
    status = Column(Enum(Status), default=Status.CREATED)
    error = Column(String)

    def __init__(self, transaction, market, transaction_type, coin, amount, price, order_id=0, status=Status.CREATED):
        self.transaction = transaction
        self.market = market
        self.type = transaction_type
        self.coin = coin
        self.amount = amount
        self.price = price
        self.order_id = order_id
        self.status = status

    def __repr__(self):
        return "<Trade(id='%s', status='%s')>" % (self.id, self.status)
