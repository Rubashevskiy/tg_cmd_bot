from collections import OrderedDict
from dataclasses import dataclass
import string
import random
from enum import Enum
from typing import Self
from module.bot.db import DB
from module.bot.config import plugin_path
from module.bot.core_plugin import CorePlugin
from module.bot.core_class import TgConnect, TgUser, TgCmdData, TgMenu, TgButton, TgPlugin, TgTxtCmd, CmdType


class CoreConfig():
    def __init__(self):
        self.connect = OrderedDict()
        self.users = OrderedDict()
        self.plugins = OrderedDict()
        self.menu = OrderedDict()
        self.text_cmd = OrderedDict()
        self.last_error = []
        self.local_modal = CorePlugin(plugin_path)

    def set_tg_connect(self, connect: TgConnect):
        self.connect[connect.session] = connect

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
        if 0==len(self.connect):
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
        data['connect'] = [connect.to_dict() for connect in list(self.connect.values())]
        data['users'] = [user.to_dict() for user in list(self.users.values())]
        data['menu'] = [menu.to_dict() for menu in list(self.menu.values())]
        data['plugins'] = [pl.to_dict() for pl in list(self.plugins.values())]
        data['text_command'] = [txt_cmd.to_dict() for txt_cmd in list(self.text_cmd.values())]
        return data

    def from_dict(self, data: dict) -> Self:
        for connect in data['connect']:
            self.set_tg_connect(TgConnect().from_dict(connect))
        for user in data['users']:
            self.set_user(TgUser().from_dict(user))
        for menu in data['menu']:
            self.set_menu(TgMenu().from_dict(menu))
        for pl in data['plugins']:
            self.set_plugin(TgPlugin().from_dict(pl))
        for txt_cmd in data['text_command']:
            self.set_text_cmd(TgTxtCmd().from_dict(txt_cmd))
        return self

    def save_to_db(self, conn_str: str):
        db = DB(conn_str=conn_str, reset_db=True)
        for connect in list(self.connect.values()):
            db.set_tg_connect(tg_conn=connect)
        for user in list(self.users.values()):
            db.set_tg_user(user=user)
        for menu in list(self.menu.values()):
            db.set_tg_menu(menu=menu)



