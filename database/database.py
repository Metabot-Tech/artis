from dynaconf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

Base = declarative_base()

Engine = create_engine(settings.DATABASE_URL.format(os.environ['POSTGRES_USER'],
                                                    os.environ['POSTGRES_PASSWORD'],
                                                    os.environ['POSTGRES_USER']))

Session = sessionmaker()
Session.configure(bind=Engine)
