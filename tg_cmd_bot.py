# Skeleton tg cmd bot

import os
import logging

from telethon import TelegramClient, events, Button
from telethon.tl.patched import Message
from telethon.errors import FloodWaitError
import asyncio

from module.config import print_log, log_path, sleep_sys_msg
from module.core import Core
from module.core_class import TgConnect, Request, SignalType, Reply, ReplyType
from module.core_exception import CoreException


py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)
py_handler = logging.FileHandler(os.path.join(log_path, 'tg_cmd_bot.log'), mode='a')
py_formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
py_handler.setFormatter(py_formatter)
py_logger.addHandler(py_handler)
if print_log: py_logger.addHandler(logging.StreamHandler())

'''Connect to the Core and initialize the telegram client'''
try:
    core = Core()
    cfg = core.get_tg_connect()
    py_logger.info(f'''RUN TG CMD BOT: <{cfg.session}>''')
    client = TelegramClient(session=cfg.session, api_id=cfg.api_id, api_hash=cfg.api_hash).start(bot_token=cfg.token)
except CoreException as e:
    py_logger.critical(f'{e.msg}')
    for s in e.data:
        py_logger.error(f'  {s}')
    exit(1)
except Exception as x:
    py_logger.critical(x.args[0])
    exit(2)


async def core_request(request: Request):
    # Processing the request and returning data
    try:
        reply = core.user_request(request)
        if reply is None:
            return
        async with client.conversation(request.chat_id) as conv:
            if ReplyType.message == reply.type:
                for msg in reply.data:
                    await conv.send_message(msg)
            elif ReplyType.error == reply.type:
                if reply.text is not None:
                    await conv.send_message(reply.text)
                    py_logger.error(f'''{reply.text}''')
                for e in reply.data:
                    py_logger.error(f'''{e}''')
            elif ReplyType.menu == reply.type:
                buttons = [[Button.inline(btn[0], btn[1])] for btn in reply.data]
                if  reply.rewrite:
                    await client.edit_message(request.username, request.msg_id, reply.text, buttons=buttons)
                else:
                    await conv.send_message(reply.text, buttons=buttons)

    except CoreException as e:
        py_logger.error(f'{e.msg}')
        for s in e.data:
            py_logger.error(f'  {s}')
    except Exception as x:
        py_logger.error(x.args[0])

async def handle_system_message():
    # Automatic sending of system messages
    while True:
        try:
            for reply in core.auto_request():
                for user in core.get_auto_users():
                    for msg in reply.data:
                        await client.send_message(user, msg)
        except Exception as e:
            py_logger.warning(f'''Error sysyem message: {e}''')
            await asyncio.sleep(sleep_sys_msg)
        await asyncio.sleep(sleep_sys_msg)


@client.on(events.NewMessage(func=lambda e: e.is_private))
async def handle_new_message(event):
    # Receiving new messages from a user
    try:
        sender = await event.get_sender()
        message = event.message
        await core_request(Request(type=SignalType.text_cmd,
                                   chat_id=message.chat.id,
                                   msg_id=message.id,
                                   username=sender.username,
                                   data=str(message.message)
                                  )
                          )
    except Exception as e:
        py_logger.error(f'''Error processing new message: {e}''')

@client.on(events.CallbackQuery())
async def handle_new_data(event):
    # Receiving new data(button click) from a user
    try:
        sender = await event.get_sender()
        await core_request(Request(type=SignalType.button,
                                   chat_id= event.chat.id,
                                   msg_id=event.message_id,
                                   username=sender.username,
                                   data=str(event.data.decode('utf-8'))
                                  )
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