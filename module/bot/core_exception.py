# Exception class using tg_bot_cmd

class CoreException(Exception):
    def __init__(self, msg: str, data: str = None):
        self.msg = msg
        self.data = data