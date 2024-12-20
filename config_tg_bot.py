import os
import json
import logging

from module.core_config import CoreConfig
from module.core_class import DbTgConn
from module.core_exception import CoreException

py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(os.path.join('.', 'logs', 'config_bot.log'), mode='a')
py_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)

# DEMO DATA
conn_str = f'''sqlite:///{os.path.join('.', 'config', 'tg_bot_db_demo.sqlite3')}'''
config_path = os.path.join('.', 'config', 'config_demo.json')

# USER DATA
#conn_str= f'''sqlite:///{os.path.join('.', 'config', 'tg_bot_db.sqlite3')}'''
#config_path = os.path.join('.', 'config', 'config.json')


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
        cfg = CoreConfig(conn_str=conn_str, reset_db=True)
        # Read config json
        data = read_json(config_path)
        # Set tg connect params
        cfg.set_tg_connect(conn_cfg=data['connect'])
    except KeyError as k:
        py_logger.critical(f''' Key not found <{k.args[0]}>''')
        exit(999)
    except CoreException as e:
        py_logger.critical(f'''{e.error}''')
        exit(1000)

if __name__ == '__main__':
    main()
