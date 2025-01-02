from collections import OrderedDict
from dataclasses import dataclass
import string
import random
import os
import json
import logging
from enum import Enum
from typing import Self

from module.bot.config import db_conn_str, plugin_path, log_path, print_log
from module.bot.core_plugin import CorePlugin
config_path_one = os.path.join('.', 'module', 'config', 'config_demo.json')
config_path_two = os.path.join('.', 'module', 'config', 'config_demo_2.json')

py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(os.path.join(log_path, 'config_bot.log'), mode='a')
py_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)
if print_log: py_logger.addHandler(logging.StreamHandler())

class CmdType(Enum):
    to_menu = 1
    to_plugin = 2

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


class CoreConfig():
    def __init__(self):
        self.config = None
        self.users = OrderedDict()
        self.plugins = OrderedDict()
        self.menu = OrderedDict()
        self.text_cmd = OrderedDict()
        self.last_error = []
        self.local_modal = CorePlugin(plugin_path)

    def set_tg_connect(self, config: TgConnect):
        self.config = config

    def set_user(self, user: TgUser):
        self.users[user.user_uid] = user

    def set_plugin(self, plugin: TgPlugin):
        self.plugins[plugin.uid] = plugin

    def set_menu(self, menu: TgMenu):
        self.menu[menu.title] = menu

    def set_text_cmd(self, cmd: TgTxtCmd):
        self.text_cmd[cmd.text] = cmd

    def get_error(self) -> list[str]:
        return self.last_error

    def check(self) -> bool:
        if self.config is None:
            self.last_error.append('Error: Connect config not found')
        if 0 == len(self.users):
            self.last_error.append('Error: Users not found')
        for m in list(self.menu.values()):
            if 0 == len(m.buttons):
                self.last_error.append(f'Error: Buttons not found in menu {m.title}')
                continue
            for b in list(m.buttons.values()):
                for c in b.cmd:
                    if CmdType.to_menu == c.cmd_type:
                        if c.cmd_uid not in self.menu:
                            self.last_error.append(f'Error: Button <{m.title}> -> <{b.text}> call not found menu <{c.cmd_uid}>')
                    elif CmdType.to_plugin == c.cmd_type:
                        if c.cmd_uid not in self.plugins:
                            self.last_error.append(f'Error: Button <{m.title}> -> <{b.text}> call not found plugin <{c.cmd_uid}>')
        if 0 == len(self.text_cmd):
            self.last_error.append('Error: Text command not found')
        else:
            for c in list(self.text_cmd.values()):
                if CmdType.to_menu == c.cmd:
                    if c.cmd_uid not in self.menu:
                        self.last_error.append(f'Error: Command <{c.text}> call not found menu <{c.cmd_uid}>')
                elif CmdType.to_plugin == b.cmd:
                    if c.cmd_uid not in self.plugins:
                        self.last_error.append(f'Error: Command <{c.text}> call not found plugin <{c.cmd_uid}>')
        for pl in list(self.plugins.keys()):
            if not self.local_modal.plugin_check(pl):
                self.last_error.append(f'Error: Plugin <{pl}>  not found in local folder')
        return 0 == len(self.last_error)

    def to_dict(self):
        data = {}
        data['connect'] = self.config.to_dict()
        data['users'] = [user.to_dict() for user in list(self.users.values())]
        data['menu'] = [menu.to_dict() for menu in list(self.menu.values())]
        data['plugins'] = [pl.to_dict() for pl in list(self.plugins.values())]
        data['text_command'] = [txt_cmd.to_dict() for txt_cmd in list(self.text_cmd.values())]
        return data

    def from_dict(self, data: dict) -> Self:
        self.set_tg_connect(TgConnect().from_dict(data['connect']))
        for user in data['users']:
            self.set_user(TgUser().from_dict(user))
        for menu in data['menu']:
            self.set_menu(TgMenu().from_dict(menu))
        for pl in data['plugins']:
            self.set_plugin(TgPlugin().from_dict(pl))
        for txt_cmd in data['text_command']:
            self.set_text_cmd(TgTxtCmd().from_dict(txt_cmd))
        return self
    
    def to_db(self, conn_str: str):
        pass


