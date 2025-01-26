# Exception class using tg_bot_cmd

class CoreException(Exception):
    def __init__(self, msg: str, data: list = []):
        self.msg = msg
        self.data = data