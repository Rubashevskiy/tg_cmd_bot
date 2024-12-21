# Class using tg_bot_cmd
import enum
from sqlalchemy import  Column, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase

class RequestType(enum.Enum):
    text = 1
    data = 2
    auto = 3

class ReplyType(enum.Enum):
    menu = 1
    message = 2
    error = 3
    cmd = 4

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

class DbCommand(Base):
    __tablename__ = "command"
    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(Integer, nullable=False)
    request_text = Column(String, nullable=False)
    reply_type = Column(Integer, nullable=False)
    reply_id = Column(Integer, nullable=False)
    sorting = Column(Integer, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("request_type", "request_text", name="uniq_cmd"),)
