import datetime
from sqlalchemy import Column, Integer, DateTime, Enum, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database.models.coins import Coins
from database.models.markets import Markets
from database.models.base import Base


class Balance(Base):
    __tablename__ = 'balances'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    transaction = relationship("Transaction", backref="balances")
    created = Column(DateTime, default=datetime.datetime.now)
    market = Column(Enum(Markets))
    coin = Column(Enum(Coins))
    amount = Column(Numeric(25, 18))

    def __init__(self, transaction, market, coin, amount):
        self.transaction = transaction
        self.market = market
        self.coin = coin
        self.amount = amount

    def __repr__(self):
        return "<Balance(id={}, coin={}, amount={})>".format(self.id, self.coin, self.amount)
