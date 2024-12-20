# Class using tg_bot_cmd

from sqlalchemy import  Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase): pass

class DbTgConn(Base):
    __tablename__ = "tg_connect"
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, nullable=False)
    api_hash = Column(String, nullable=False)
    session = Column(String, nullable=False)
    token = Column(String, nullable=False)
    root_uid = Column(String, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("session", name="uniq_session"),)
