import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'catalog_user'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, nullable=False, unique=True)


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    @property
    def serialize(self):
        ''' Returns the category data in easily serializable format '''
        return {
            'name': self.name,
            'id': self.id
        }


class CategoryItem(Base):
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String(500))
    date = Column(DateTime, nullable=False)

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('catalog_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        ''' Returns the category item data in easily serializable format '''
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'date': self.date,
            'category_id': self.category_id
        }


#engine = create_engine('sqlite:///itemcatalog.db')
engine = create_engine('postgresql:///itemcatalog')
Base.metadata.create_all(engine)
