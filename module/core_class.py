import enum
from collections import OrderedDict
from dataclasses import dataclass
from typing import Self

from sqlalchemy import  Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship

from module.core_exception import CoreException

class ReplyType(enum.Enum):
    message = 1
    error = 2
    menu = 3

class SignalType(enum.Enum):
    button = 1
    text_cmd = 2
    auto = 3

@dataclass
class Request:
    type: SignalType
    chat_id: int
    msg_id: int
    username: str
    data: str

@dataclass
class Reply:
    type: ReplyType
    text: str
    data: list
    rewrite: bool = False

class SlotType(enum.Enum):
    menu = 1
    plugin = 2

@dataclass
class TgConnect:
    api_id : int = None
    api_hash : str = None
    session : str = None
    token : str = None
    info: str = None

    def from_dict(self, data: dict) -> Self:
        try:
            self.api_id = data['api_id']
            self.api_hash = data['api_hash']
            self.session = data['session']
            self.token = data['token']
            self.info = data['info'] if 'info' in data else None
            return self
        except KeyError as k:
            raise CoreException(f'TgConnect: KeyError: {k.args[0]}')

@dataclass
class TgUser:
    name: str = None
    auto_msg: bool = None
    info: str = None

    def from_dict(self, data: dict) -> Self:
        try:
            self.name = data['name']
            self.auto_msg = data['auto_msg']
            self.info = data['info'] if 'info' in data else None
            return self
        except KeyError as k:
            raise CoreException(f'TgUser: KeyError: {k.args[0]}')

@dataclass
class TgObject:
    text: str = None
    slot_type: SlotType = None
    slot_uid: str = None
    params: dict = None
    info: str = None
    data: str = None

    def from_dict(self, data: dict) -> Self:
        try:
            self.text = data['text']
            self.slot_type = SlotType[data["slot_type"]]
            self.slot_uid = data["slot_uid"]
            self.params = data['params'] if 'params' in data else {}
            self.info = data['info'] if 'info' in data else None
            return self
        except KeyError as k:
            raise CoreException(f'TgObject: KeyError: {k.args[0]}')

@dataclass
class TgButton(TgObject):
    pass

@dataclass
class TgTextCmd(TgObject):
    pass

@dataclass
class TgMenu:
    text: str = None
    info: str = None
    buttons: OrderedDict = None

    def __post_init__(self):
        self.buttons = OrderedDict()

    def add_button(self, btn: TgButton):
        self.buttons[btn.text] = btn

    def get_all_buttons(self) -> list[TgButton]:
        return list(self.buttons.values())

    def from_dict(self, data: dict)-> Self:
        try:
            self.text = data['text']
            self.info = self.info = data['info'] if 'info' in data else None
            for btn in data['buttons']:
                self.add_button(TgButton().from_dict(btn))
            return self
        except KeyError as k:
            raise CoreException(f'TgMenu: KeyError: {k.args[0]}')

@dataclass
class TgAuto:
    plugin_uid: str = None
    params: dict = None
    info: str = None

    def from_dict(self, data: dict) -> Self:
        try:
            self.plugin_uid = data['plugin_uid']
            self.params = data['params'] if 'params' in data else {}
            self.info = data['info'] if 'info' in data else None
            return self
        except KeyError as k:
            raise CoreException(f'TgUser: KeyError: {k.args[0]}')

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
    name = Column(String, nullable=False)
    auto_msg = Column(Integer, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("name", name="uniq_users"),)

class DbTgMenu(Base):
    __tablename__ = "tg_menu"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("text", name="uniq_menu"),)

class DbTgButton(Base):
    __tablename__ = "tg_buttons"
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey(DbTgMenu.id),nullable=False)
    text = Column(String, nullable=False)
    data = Column(String, nullable=False)
    sorting = Column(Integer, nullable=False)
    slot_type = Column(Integer, nullable=False)
    slot_uid = Column(String, nullable=False)
    params = Column(String, nullable=True)
    info = Column(String, nullable=True)
    menu = relationship("DbTgMenu", backref='buttons')
    __table_args__ = (UniqueConstraint("data", name="uniq_btn"), UniqueConstraint("menu_id", "text", name="uniq_menu_btn"),)

class DbTgTextCmd(Base):
    __tablename__ = "tg_txt_cmd"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    slot_type = Column(Integer, nullable=False)
    slot_uid = Column(String, nullable=False)
    params = Column(String, nullable=True)
    info = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("text", name="uniq_cmd_text"),)

class DbTgAuto(Base):
    __tablename__ = "tg_auto"
    id = Column(Integer, primary_key=True, index=True)
    plugin_uid = Column(String, nullable=False)
    params = Column(String, nullable=True)
    info = Column(String, nullable=True)