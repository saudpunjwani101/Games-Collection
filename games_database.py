import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, Unicode, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class User(Base):
	__tablename__ = 'user'

	username = Column(String(100), nullable=False, primary_key=True)
	password = Column(Unicode(100), nullable=False)

class Console(Base):
	__tablename__ = 'console'

	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=False)
	company = Column(String(50))
	user_name = Column(String(100), ForeignKey('user.username'))
	user = relationship(User)

class Game(Base):
	__tablename__ = 'game'

	id = Column(Integer, primary_key=True)
	name = Column(String(100), nullable=False)
	description = Column(String(100), nullable=False)
	developed_by = Column(String(100))
	released_year = Column(String(50))
	ratings = Column(Integer, nullable=False)
	console_id = Column(Integer, ForeignKey('console.id'))
	console=relationship(Console)
	user_name = Column(String(100), ForeignKey('user.username'))
	user = relationship(User)


class UserPhoto(Base):
	__tablename__ = 'userphoto'

	id = Column(Integer, primary_key=True)
	filename = Column(String(100))
	user_name = Column(String(100), ForeignKey('user.username'))
	user = relationship(User)


class GamePhoto(Base):
	__tablename__ = 'gamephoto'

	id = Column(Integer, primary_key=True)
	filename = Column(String(100))
	console_id = Column(Integer, ForeignKey('console.id'))
	console = relationship(Console)
	game_id = Column(Integer, ForeignKey('game.id'))
	game = relationship(Game)


engine = create_engine('sqlite:///gamescollection.db')
Base.metadata.create_all(engine)
