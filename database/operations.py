from database.models.transaction import Transaction
from database.models.trade import Trade
from database.models.types import Types
from database.models.status import Status
from database.database import Session


def create_transaction():
    return upsert_transaction(Transaction())


def upsert_transaction(transaction):
    return _upsert_data(transaction)


def count_transactions():
    session = Session()

    try:
        count = session.query(Transaction).count()
    except:
        raise
    finally:
        session.close()
    return count


def fetch_pending_sells():
    session = Session()

    try:
        trades = session.query(Trade).filter(Trade.type == Types.SELL, Trade.status == Status.ONGOING).all()
    except:
        raise
    finally:
        session.close()
    return trades


def upsert_trade(trade):
    return _upsert_data(trade)


def upsert_balance(balance):
    return _upsert_data(balance)


def _upsert_data(data):
    session = Session()

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
