from module.core_class import Reply, ReplyType

uid = str('plugin_2')
info = str(f'Plugin info: <{uid}>')

class Plugin():
    def __init__(self, args: list = [], params: dict = None) -> None:
        self.params = params

    # Return plugin UID
    @staticmethod
    def get_uid() -> str:
        return uid

    # Return plugin Info
    @staticmethod
    def get_info() -> str:
        return info

    # The main method of execution
    def run(self) -> Reply:
        return Reply(type=ReplyType.message, text='', data=[f'Plugin <{uid}> test msg.'])