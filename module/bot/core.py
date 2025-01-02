from module.bot.db import DB
from module.bot.core_class import Request, RequestType, Reply, ReplyType, CmdType
from module.bot.core_class import Base, DbTgConn, DbCommand, DbMenu, DbButtons
from module.bot.core_exception import CoreException

class Core():
    def __init__(self):
        self.db = DB()

    def get_tg_connect(self) -> DbTgConn:
        return self.db.get_tg_connect()

    def request(self, request: Request) -> list[Reply]:
        # Processing a request from a user
        if not self.db.check_user(request.username):
            return [Reply(type=ReplyType.error, text='Access Denied', data = [f'''<{request.username}> <{request.type.name}> <{request.data}>'''])]
        cmd = self.db.get_commands(request.type, request.data, request.username)
        if 0 < len(cmd):
            pass
        else:
            return [Reply(type=ReplyType.error, text=f'''Command not found''', data = [f'''<{request.username}> <{request.type.name}> <{request.data}>'''])]
