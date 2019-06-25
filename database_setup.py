from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """
    Registered user information is stored in db
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Catalog(Base):
    """
    Registered catalog information is stored in db
    """
    __tablename__ = 'catalog'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    items = relationship("Item", cascade="delete")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name, 
        }


class Item(Base):
    """
    Registered item information is stored in db
    """
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))

    catalog_id = Column(Integer, ForeignKey('catalog.id'))
    catalog = relationship(Catalog)
    
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)    

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'cat_id': self.catalog_id,
            'description': self.description,
            'id': self.id,
            'title': self.name,            
        }


engine = create_engine('sqlite:///catalogwithusers.db')


Base.metadata.create_all(engine)