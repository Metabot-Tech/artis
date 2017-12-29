import datetime
from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database.models.coins import Coins
from database.models.markets import Markets
from database.models.status import Status
from database.database import Base


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship("Transaction", backref="trades")
    order_id = Column(Integer, default=0)  # TODO: remove default when database rerun
    created = Column(DateTime, default=datetime.datetime.now)
    updated = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    market = Column(Enum(Markets))
    sell_amount = Column(Numeric(25, 18))
    sell_coin = Column(Enum(Coins))
    buy_amount = Column(Numeric(25, 18))
    buy_coin = Column(Enum(Coins))
    status = Column(Enum(Status), default=Status.CREATED)
    error = Column(String)

    def __init__(self, transaction, market, sell_amount, sell_coin, buy_amount, buy_coin):
        self.transaction = transaction
        self.market = market
        self.sell_amount = sell_amount
        self.sell_coin = sell_coin
        self.buy_amount = buy_amount
        self.buy_coin = buy_coin

    def __repr__(self):
        return "<Trade(id='%s', status='%s')>" % (self.id, self.status)
