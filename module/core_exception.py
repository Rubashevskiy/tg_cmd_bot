# Exception class using tg_bot_cmd

class CoreException(Exception):
    def __init__(self, error: str):
        self.error = error