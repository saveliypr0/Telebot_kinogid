from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class User(Base):
    __tablename__ = 'favorite_films'

    id = Column(Integer, primary_key=True)
    id_usera = Column(Integer, nullable=False)
    favor = Column(String(50), nullable=False)

    def __init__(self, id_usera, favor):
        self.id_usera = id_usera
        self.favor = favor

    def __repr__(self):
        return f"<User(id_usera='{self.id_usera}', favor='{self.favor}')>"