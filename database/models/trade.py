import datetime
from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from database.models.coins import Coins
from database.models.markets import Markets
from database.models.status import Status
from database.models.transaction import Transaction

Base = declarative_base()


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    transaction = Column(Integer, ForeignKey(Transaction.id)),
    order_id = Column(Integer)
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    market = Column(Enum(Markets))
    sell_amount = Column(Numeric(25, 18))
    sell_coin = Column(Enum(Coins))
    buy_amount = Column(Numeric(25, 18))
    buy_coin = Column(Enum(Coins))
    status = Column(Enum(Status), default=Status.CREATED)
    error = Column(String)

    def __init__(self, transaction, market, sell_amount, sell_coin):
        self.transaction = transaction
        self.market = market
        self.sell_amount = sell_amount
        self.sell_coin = sell_coin

    def __repr__(self):
        return "<Trade(id='%s', status='%s')>" % (self.id, self.status)
