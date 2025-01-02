import os
import json
import logging

from module.bot.core_config import CoreConfig
from module.bot.core_exception import CoreException
from module.bot.config import db_conn_str, log_path, print_log


config_path = os.path.join('.', 'config_json', 'config.json')

py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(os.path.join(log_path, 'config_bot.log'), mode='a')
py_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)
if print_log: py_logger.addHandler(logging.StreamHandler())

def read_json(path: str) -> dict:
    try:
        with open(path, encoding='utf-8') as f:
            d = json.load(f)
            return d
    except FileNotFoundError:
        py_logger.critical(f'''File not found {path}''')
        exit(1)
    except json.decoder.JSONDecodeError:
        py_logger.critical(f'''File not json format {path}''')
        exit(2)


def save_json(data: dict, path: str):
    try:
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        py_logger.critical(f'''File not found {path}''')
        exit(1)
    except json.decoder.JSONDecodeError:
        py_logger.critical(f'''File not json format {path}''')
        exit(2)

def main() -> None:
    try:
        py_logger.info(f'''Run app. DB: {db_conn_str} Config: {config_path}''')
        cfg = CoreConfig().from_dict(read_json(config_path))
        if not cfg.check():
            for e in cfg.get_error():
                print(e)
            py_logger.critical(f'''Config not correct''')
        else:
            cfg.save_to_db(db_conn_str)
    except CoreException as e:
        py_logger.critical(f'''{e.error}''')
        exit(1000)

if __name__ == '__main__':
    main()
