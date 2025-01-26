from module.core_class import Reply, ReplyType
import argparse

uid = str('plugin_argv')
info = str(f'Plugin info: <{uid}>')

class Plugin():
    def __init__(self, args: list = [], params: dict = {}) -> None:
        self.params = params
        self.help = str('')
        self.args = self.__arg_parse__(args)

    def __arg_parse__(self, args):
        parser = argparse.ArgumentParser(
                    prog='PluginName',
                    description='What the plugin does',
                    epilog='Text at the bottom of help',
                    add_help=False)
        parser.add_argument('-t', '--test', dest='test', action='store_true', required=False)
        parser.add_argument('-h', '--help', dest='help', action='store_true', required=False)
        self.help = parser.format_help()
        return parser.parse_known_args(args)[0]

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
        if self.args.help:
            return Reply(type=ReplyType.message, text='', data=[self.help])
        else:
            return Reply(type=ReplyType.message, text='', data=[f'Plugin <{uid}> test msg.', f'argv parse {self.args.test}'])