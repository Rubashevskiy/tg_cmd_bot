# Class using tg_bot_cmd
import enum
from dataclasses import dataclass
from sqlalchemy import  Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase

class RequestType(enum.Enum):
    text = 1
    data = 2
    auto = 3

class ReplyType(enum.Enum):
    menu = 1
    message = 2
    error = 3

class CmdType(enum.Enum):
    menu = 1
    plugin = 2

@dataclass
class TgConfig:
    api_id: int
    api_hash: str
    session: str
    token: str
    root_uid: str
    info: str

@dataclass
class Request:
    type: RequestType
    chat_id: int
    msg_id: int
    username: str
    data: str

@dataclass
class Reply:
    type: ReplyType
    text: str
    data: list

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
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("request_type", "request_text", name="uniq_cmd"),)

class DbMenu(Base):
    __tablename__ = "menu"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("title", name="uniq_menu"),)

class DbButtons(Base):
    __tablename__ = "buttons"
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey(DbMenu.id),nullable=False)
    btn_text = Column(String, nullable=False)
    btn_data= Column(String, nullable=False)
    sorting = Column(Integer, nullable=False)
    info = Column(String, nullable=True)

class DbPlugin(Base):
    __tablename__ = "plugin"
    id = Column(Integer, primary_key=True, index=True)
    plugin_uid = Column(String, nullable=False)
    plugin_data = Column(String, nullable=False)
    sorting = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint("plugin_uid", "plugin_data", name="uniq_plugin"),)