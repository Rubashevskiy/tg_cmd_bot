# Class using tg_bot_cmd
import enum
from dataclasses import dataclass
from collections import OrderedDict
import string
import random
from typing import Self
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
    to_menu = 1
    to_plugin = 2

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

@dataclass
class TgConnect:
    api_id : int = None
    api_hash : str = None
    session : str = None
    token : str = None
    info : str = None

    def from_dict(self, data: dict) -> Self:
        self.api_id = data['api_id']
        self.api_hash = data['api_hash']
        self.session = data['session']
        self.token = data['token']
        self.info = data['info'] if 'info' in data else None
        return self

    def to_dict(self) -> dict:
        data = {'api_id' : self.api_id,
                'api_hash' : self.api_hash,
                'session' : self.session,
                'token' : self.token
               }
        if self.info is not None:
            data['info'] = self.info
        return data

@dataclass
class TgUser():
    user_uid: str = None
    info: str = None

    def from_dict(self, data: dict) -> Self:
        self.user_uid = data['user_uid']
        self.info = data['info'] if 'info' in data else None
        return self

    def to_dict(self) -> dict:
        data = {'user_uid' : self.user_uid}
        if self.info is not None:
            data['info'] = self.info
        return data

@dataclass
class TgCmdData:
    cmd_type: CmdType = None
    cmd_uid: str = None

    def from_dict(self, data: dict) -> Self:
        if 'to_menu' in data:
            cmd_type = CmdType.to_menu
            cmd_uid = data['to_menu']
        elif 'to_plugin' in data:
            cmd_type = CmdType.to_plugin
            cmd_uid = data['to_plugin']
        self.cmd_type = cmd_type
        self.cmd_uid = cmd_uid
        return self

    def to_dict(self) -> dict:
        if CmdType.to_menu == self.cmd_type:
            return {'to_menu' : self.cmd_uid}
        elif CmdType.to_plugin == self.cmd_type:
            return {'to_plugin' : self.cmd_uid}

@dataclass
class TgButton:
    text: str = None
    data: str = None
    info: str = None

    def __post_init__(self):
        if self.data is None:
            self.data = self.__data_generate__()
        self.cmd = []

    def __data_generate__(self) -> str:
        all_symbols = string.ascii_uppercase + string.digits
        return f'''{''.join(random.choice(all_symbols) for _ in range(8))}'''

    def set_cmd(self, cmd: TgCmdData):
        self.cmd.append(cmd)

    def from_dict(self, data: dict) -> Self:
        self.text=data['text']
        self.data=data['data'] if 'data' in data else self.__data_generate__()
        self.info=data['info'] if 'info' in data else None
        for cmd in data['cmd']:
            self.set_cmd(TgCmdData().from_dict(cmd))
        return self

    def to_dict(self) -> dict:
        data = {'text' : self.text,
                'data' : self.data
               }
        data['cmd'] = [cmd.to_dict() for cmd in self.cmd]
        if self.info is not None:
            data['info'] = self.info
        return data

@dataclass
class TgMenu():
    title: str = None
    info: str = None

    def __post_init__(self):
        self.buttons = OrderedDict()

    def set_button(self, button: TgButton):
        self.buttons[button.text] = button

    def from_dict(self, data: dict) -> Self:
        self.title=data['title']
        self.info=data['info'] if 'info' in data else None
        for btn in data['buttons']:
            self.set_button(TgButton().from_dict(btn))
        return self

    def to_dict(self) -> dict:
        data = {'title' : self.title}
        data['buttons'] = [btn.to_dict() for btn in self.buttons.values()]
        if self.info is not None:
            data['info'] = self.info
        return data

@dataclass
class TgTxtCmd:
    text: str = None
    info: str = None

    def __post_init__(self):
        if self.text is not None:
            self.text = str(self.text).upper()
        self.cmd = []

    def set_cmd(self, cmd: TgCmdData):
        self.cmd.append(cmd)

    def from_dict(self, data: dict) -> Self:
        self.text=str(data['text']).upper()
        self.info=data['info'] if 'info' in data else None
        for cmd in data['cmd']:
            self.cmd.append(TgCmdData().from_dict(cmd))
        return self

    def to_dict(self) -> dict:
        data = {'text' : self.text}
        data['cmd'] = [cmd.to_dict() for cmd in self.cmd]
        if self.info is not None:
            data['info'] = self.info
        return data

@dataclass
class TgPlugin:
    uid: str = None
    config: dict = None
    info: str = None

    def from_dict(self, data: dict) -> Self:
        self.uid=data['uid']
        self.config = data['config'] if 'config' in data else None
        self.info=data['info'] if 'info' in data else None
        return self

    def to_dict(self) -> dict:
        data = {'uid' : self.uid}
        if self.config is not None:
            data['config'] = self.config
        if self.info is not None:
            data['info'] = self.info
        return data

class Base(DeclarativeBase): pass

class DbTgConnect(Base):
    __tablename__ = "tg_connect"
    id = Column(Integer, primary_key=True, index=True)
    api_id = Column(Integer, nullable=False)
    api_hash = Column(String, nullable=False)
    session = Column(String, nullable=False)
    token = Column(String, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("session", name="uniq_session"),)

class DbTgUser(Base):
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

 
class DbButton(Base):
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
    btn_id = Column(Integer, ForeignKey(DbButton.id),nullable=False)
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
    __table_args__ = (UniqueConstraint("uid", "config", name="uniq_plugin"),)