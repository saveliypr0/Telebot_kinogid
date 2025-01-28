from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base

engine = create_engine('sqlite:///users_date.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
