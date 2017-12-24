from database.models.transaction import Transaction
import database.database as db


def create_transaction():
    return update_transaction(Transaction())


def update_transaction(transaction):
    session = db.session()

    try:
        session.add(transaction)
        session.commit()
        session.refresh(transaction)
    except:
        session.rollback()
        raise
    finally:
        session.close()

    return transaction
