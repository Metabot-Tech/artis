import os
from dynaconf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models.transaction import Transaction
from .models.trade import Trade
from .models.types import Types
from .models.status import Status


class Database(object):
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL.format(os.environ['POSTGRES_USER'],
                                                                 os.environ['POSTGRES_PASSWORD'],
                                                                 os.environ['POSTGRES_USER']))

        self.session = sessionmaker()
        self.session.configure(bind=self.engine)

    def create_transaction(self):
        return self.upsert_transaction(Transaction())

    def upsert_transaction(self, transaction):
        return self._upsert_data(transaction)

    def count_transactions(self):
        session = self.session()

        try:
            count = session.query(Transaction).count()
        except:
            raise
        finally:
            session.close()
        return count

    def fetch_pending_sells(self):
        session = self.session()

        try:
            trades = session.query(Trade).filter(Trade.type == Types.SELL, Trade.status == Status.ONGOING).all()
        except:
            raise
        finally:
            session.close()
        return trades

    def upsert_trade(self, trade):
        return self._upsert_data(trade)

    def upsert_balance(self, balance):
        return self._upsert_data(balance)

    def _upsert_data(self, data):
        session = self.session()

        try:
            session.add(data)
            session.commit()
            session.refresh(data)
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return data
