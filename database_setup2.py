import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# create tables for user, list and item

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(80), nullable=False)

class ToDoList(Base):
    __tablename__ = 'to_do_list'

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    description = Column(String(150))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)    

    @property
    def serialize(self):
        return {
         	'id': self.id,
            'title': self.title,
            'description': self.description,
        }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    list_id = Column(Integer, ForeignKey('to_do_list.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)  
    to_do_list = relationship(ToDoList)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'list_id': self.id,
        }

engine = create_engine('sqlite:///toDoListMaker2.db')

Base.metadata.create_all(engine)