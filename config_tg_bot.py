import os
import json
import logging

from module.core_db_config import CoreDbConfig
from module.core_class import TgConnect, TgUser, TgMenu, TgButton, TgTextCmd, SlotType, TgAuto
from module.config import db_conn_str
from module.core_exception import CoreException

log_path = os.path.join('.', 'logs')
config_path = os.path.join('.', 'load_config', 'config.json')


py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(os.path.join(log_path, 'config_bot.log'), mode='a')
py_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)
py_logger.addHandler(logging.StreamHandler())

def read_json(path: str) -> dict:
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
            return d
    except FileNotFoundError:
        raise CoreException(f'''File not found {path}''')
    except json.decoder.JSONDecodeError:
        raise CoreException(f'''File not json format {path}''')


def main() -> None:
    try:
        data = read_json(config_path)
        config = CoreDbConfig(reset=True)
        for conn in data['connect']:
            config.add_connect(TgConnect().from_dict(conn))
        for user in data['users']:
            config.add_user(TgUser().from_dict(user))
        for menu in data['menu']:
            config.add_menu(TgMenu().from_dict(menu))
        for txt_cmd in data['text_command']:
            config.add_text_cmd(TgTextCmd().from_dict(txt_cmd))
        for auto in data['auto']:
            config.add_tg_auto(TgAuto().from_dict(auto))

        # Check Config
        if  not config.check_errors_integrity():
            py_logger.error('=== Configuration errors ===')
            for e in config.get_errors():
                py_logger.error(e)
            exit(10)
        else:
            py_logger.info(f'''Load config <{config_path}> OK''')
    except CoreException as e:
        py_logger.error(f'{e.msg}')
        for s in e.data:
            py_logger.error(f'  {s}')

if __name__ == '__main__':
    main()

