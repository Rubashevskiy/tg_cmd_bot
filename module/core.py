from module.core_class import TgConnect, Request, Reply, ReplyType, SignalType, SlotType
from module.core_db_config import CoreDbConfig
from module.core_plugin import CorePlugin
from module.core_exception import CoreException

class Core():
    def __init__(self):
        self.db = CoreDbConfig(reset=False)
        self.pl = CorePlugin()
        self.last_menu = None
        if not self.db.check_errors_integrity():
            raise CoreException(msg='Check errors integrity', data=self.db.get_errors())

    def get_tg_connect(self) -> TgConnect:
        return self.db.get_connect()

    def get_auto_users(self) -> list[str]:
        return self.db.get_auto_users()

    def user_request(self, request: Request) -> list[Reply]:
        if not self.db.check_user(request.username):
            return Reply(type=ReplyType.error, text=None, data=[f'The <{{request.username}}> is prohibited', f'<{request.data}>'])
        else:
            data = request.data.split(' ')
            if request.type == SignalType.text_cmd:
                rwr_flg = False
                cmd = self.db.get_text_cmd(str(data[0]).upper())
            elif request.type == SignalType.button:
                rwr_flg = True
                cmd = self.db.get_button(str(data[0]).upper())
            if cmd is not None:
                if SlotType.menu == cmd.slot_type:
                    return self.get_reply_menu(cmd.slot_uid, rwr_flg)
                elif SlotType.plugin == cmd.slot_type:
                    return self.get_reply_plugin(cmd.slot_uid, data[1:], cmd.params)
            else:
                return Reply(type=ReplyType.error,text='Command not found', data=[f'<{request.data}>'])

    def auto_request(self) -> list[Reply]:
        result = []
        for cmd in self.db.get_all_tg_auto():
            reply = self.get_reply_plugin(cmd.plugin_uid, [], cmd.params)
            if reply is not None:
                result.append(reply)
        return result

    def get_reply_menu(self, menu_text: str, rwr_flg: bool) -> Reply:
        self.last_menu = menu_text
        tg_menu = self.db.get_menu(menu_text=menu_text)
        if tg_menu is None:
            raise CoreException(f'Configuration error. Menu {menu_text} not found')
        return Reply(type=ReplyType.menu, text=tg_menu.text, data=[(btn.text, btn.data) for btn in tg_menu.get_all_buttons()], rewrite=rwr_flg)

    def get_reply_plugin(self, uid: str, args: list = [], params: dict = {}) -> Reply:
        module = self.pl.load(uid)
        if module is None:
            raise CoreException(f'Configuration error. Module {uid} not found')
        pl = module.Plugin(args, params)
        return pl.run()
