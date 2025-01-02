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
    file = 3
    image = 4
    error = 5

class CmdType(enum.Enum):
    menu = 1
    plugin = 2


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
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("session", name="uniq_session"),)

class DbTgUsers(Base):
    __tablename__ = "tg_users"
    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("user_uid", name="uniq_users"),)

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
    btn_data = Column(String, nullable=False)
    sorting = Column(Integer, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("menu_id", "btn_text", name="uniq_btn"),)

class DbButtonCmd(Base):
    __tablename__ = "button_cmd"
    id = Column(Integer, primary_key=True, index=True)
    btn_id = Column(Integer, ForeignKey(DbButtons.id),nullable=False)
    cmd_type = Column(Integer, nullable=False)
    cmd_id = Column(Integer, nullable=False)
    sorting = Column(Integer, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("btn_id", "cmd_type", "cmd_id", name="uniq_btn_cmd"),)

class DbTextCmd(Base):
    __tablename__ = "text_command"
    id = Column(Integer, primary_key=True, index=True)
    cmd_text = Column(String, nullable=False)
    cmd_type = Column(Integer, nullable=False)
    cmd_id = Column(Integer, nullable=False)
    sorting = Column(Integer, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("cmd_text", "cmd_type", "cmd_id", name="uniq_txt_cmd"),)

class DbPlugin(Base):
    __tablename__ = "plugins"
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, nullable=False)
    config = Column(String, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("uid", "data", "config", name="uniq_plugin"),)