import os

print_log = True
sleep_sys_msg = 300
log_path = os.path.join('.', 'logs')

db_conn_str= f'''sqlite:///{os.path.join('.', 'db', 'tg_bot_db_demo.sqlite3')}'''
session = 'tg_cmd_bot'
plugin_path = os.path.join('.', 'plugins')