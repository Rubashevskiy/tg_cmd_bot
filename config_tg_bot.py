import os
import json
import logging

from module.core_config import CoreConfig
from module.core_class import TgConfig
from module.core_exception import CoreException
from module.core_plugin_manager import CorePluginManager

conn_str = f'''sqlite:///{os.path.join('.', 'config', 'tg_bot_db_demo.sqlite3')}'''
config_path = os.path.join('.', 'config', 'config.json')

# PRINT LOG CONSOLE
print_log = True

py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(os.path.join('.', 'logs', 'config_bot.log'), mode='a')
py_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)
if print_log:
    py_logger.addHandler(logging.StreamHandler())

def read_json(path: str) -> dict:
    try:
        with open(path) as f:
            d = json.load(f)
            return d
    except FileNotFoundError:
        py_logger.critical(f'''File not found {path}''')
        exit(1)
    except json.decoder.JSONDecodeError:
        py_logger.critical(f'''File not json format {path}''')
        exit(2)

def main() -> None:
    try:
        py_logger.info(f'''Run app. DB: {conn_str} Config: {config_path}''')
        # Open db
        core = CoreConfig(conn_str=conn_str, reset_db=True)
        # Read config json
        data = read_json(config_path)
        # Set tg connect params
        core.set_tg_connect(TgConfig(api_id=data['connect']['api_id'],
                                     api_hash=data['connect']['api_hash'],
                                     session=data['connect']['session'],
                                     token=data['connect']['token'],
                                     root_uid=data['connect']['root_uid'],
                                     info=data['connect']['info']
                                    )
                           )
        # Set menu
        for menu in data['menu']:
            info = menu['info'] if 'info' in menu else None
            core.set_menu(menu['title'], info)
        # Set plugins
        for pl in data['plugins']:
            pl_data = pl['data'] if 'data' in pl else None
            core.set_plugin()
    except KeyError as k:
        py_logger.critical(f''' Key not found <{k.args[0]}>''')
        exit(999)
    except CoreException as e:
        py_logger.critical(f'''{e.error}''')
        exit(1000)

if __name__ == '__main__':
    main()
