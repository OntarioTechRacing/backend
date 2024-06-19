from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

URL_DATABASE = ''

engine = create_engine(URL_DATABASE, echo=True)

SessionLocal = sessionmaker(autcommit=False, autoflush=False, bind=engine)

Base = declarative_base()
