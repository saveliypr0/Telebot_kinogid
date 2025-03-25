from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class User_favor(Base):
    __tablename__ = 'favorite_films'

    id = Column(Integer, primary_key=True)
    id_user = Column(Integer)
    favor = Column(String(50))


    def __repr__(self):
        return f"<User(id_usera='{self.id_user}', favor='{self.favor}')>"