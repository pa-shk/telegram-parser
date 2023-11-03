import json
from telethon import TelegramClient, sync

with open('config.json') as f:
    config = json.load(f)


API_ID = config['api_id']
API_HASH = config['api_hash']
CHAT_NAME = config['chat_name']


client = TelegramClient('session_name', API_ID, API_HASH)
client.start()


chats = client.get_dialogs()

chat = None
for cht in chats:
    if cht.name == CHAT_NAME:
        chat = cht
        break
else:
    raise ValueError('Chat with this name does not exist')


parsed_chat = {}
for message in client.get_messages(chat, limit=50):
    parsed_chat[message.id] = [message.from_id.user_id, message.text, message.reply_to_msg_id]


print(parsed_chat)
