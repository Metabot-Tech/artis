from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Enum, Numeric, ForeignKey
from models.database.status import Status
from models.database.markets import Markets
from models.database.coins import Coins
from models.database.transaction import Transaction

Base = declarative_base()


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    transaction = Column(Integer, ForeignKey(Transaction.id)),
    created = Column(DateTime)
    updated = Column(DateTime)
    market = Column(Enum(Markets))
    sell_amount = Column(Numeric(25, 18))
    sell_coin = Column(Enum(Coins))
    buy_amount = Column(Numeric(25, 18))
    buy_coin = Column(Enum(Coins))
    status = Column(Enum(Status))
    error = Column(String)

    def __repr__(self):
        return "<Trade(id='%s', status='%s')>" % (self.id, self.status)
