import os

# LOG config
print_log = True
log_path = os.path.join('.', 'logs')

# Plugins
plugin_path = os.path.join('.', 'plugins')

# DB config
db_conn_str= f'''sqlite:///{os.path.join('.', 'db', 'tg_bot_db.sqlite3')}'''
session = "tg_cmd_bot"

