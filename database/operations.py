from database.models.transaction import Transaction
from database.database import Session


def create_transaction():
    return upsert_transaction(Transaction())


def upsert_transaction(transaction):
    return _upsert_data(transaction)


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
