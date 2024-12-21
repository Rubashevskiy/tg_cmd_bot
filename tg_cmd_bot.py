# Skeleton tg cmd bot

import os
import logging

from telethon import TelegramClient, events, Button
from telethon.tl.patched import Message
from telethon.errors import FloodWaitError
import asyncio

from module.core import Core
from module.core_class import RequestType, ReplyType
from module.core_exception import CoreException

# DEMO DATA
#conn_str = f'''sqlite:///{os.path.join('.', 'config', 'tg_bot_db_demo.sqlite3')}'''
#session = "str_session_name"

# USER DATA
conn_str= f'''sqlite:///{os.path.join('.', 'config', 'tg_bot_db.sqlite3')}'''
session = "tg_cmd_bot"

py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(os.path.join('.', 'logs', 'tg_cmd_bot.log'), mode='a')
py_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)

'''Connect to the Core and initialize the telegram client'''
try:
    py_logger.info(f'''RUN TG CMD BOT<{session}>: DB <{conn_str}>''')
    core = Core(conn_str=conn_str)
    cfg = core.get_tg_connect(session)
    client = TelegramClient(session=cfg['session'],
                            api_id=cfg['api_id'],
                            api_hash=cfg['api_hash']
                           ).start(bot_token=cfg['token'])
except CoreException as e:
    py_logger.critical(e.error)
    exit(1)
except Exception as x:
    py_logger.critical(x.args[0])
    exit(2)


async def core_request(request: dict):
    # Processing the request and returning data
    try:
        async with client.conversation(request['chat_id']) as conv:
            for reply in core.request(request):
                if ReplyType.message == reply['type']:
                    for msg in reply['message']:
                        await conv.send_message(msg)
                elif ReplyType.error == reply['type']:
                    for err in reply['error']:
                        await conv.send_message(err)
                        py_logger.error(f'''<{request['username']}> {err} <{request['type']}> <{request['data']}>''')
                elif ReplyType.menu == reply['type']:
                    pass
    except CoreException as e:
        py_logger.error(e.error)
        exit(4)

async def handle_system_message():
    # Automatic sending of system messages
    while True:
        try:
            pass
        except Exception as e:
            py_logger.warning(f'''Error sending message: {e}''')
            await asyncio.sleep(5)
        await asyncio.sleep(5)


@client.on(events.NewMessage(func=lambda e: e.is_private))
async def handle_new_message(event):
    # Receiving new messages from a user
    try:
        sender = await event.get_sender()
        username = sender.username
        if username != cfg['root_uid']:
            py_logger.warning(f'''User <{username}> access deny''')
            return
        message = event.message
        await core_request({"type"     : RequestType.text,
                            "chat_id"  : message.chat.id,
                            "msg_id"   : message.id,
                            "username" : username,
                            "data"     : str(message.message).upper()
                           }
                          )
    except Exception as e:
        py_logger.error(f'''Error processing new message: {e}''')

@client.on(events.CallbackQuery())
async def handle_new_data(event):
    # Receiving new data(button click) from a user
    try:
        sender = await event.get_sender()
        username = sender.username
        if username != cfg['root_uid']:
            py_logger.warning(f'''User <{username}> access deny''')
            return
        message = event.message
        await core_request({"type"     : RequestType.data,
                            "chat_id"  : message.chat.id,
                            "msg_id"   : message.message_id,
                            "username" : username,
                            "data"     : str(event.data.decode('utf-8')).upper()
                           }
                          )
    except Exception as e:
        py_logger.error(f'''Error processing new data: {e}''')

async def main():
    try:
        await handle_system_message()
    except FloodWaitError as e:
        py_logger.error(f'''Account blocked! Try again in {e.seconds} seconds''')
        return
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(
            main()
        )