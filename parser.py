from datetime import datetime
from collections import deque
import json
from telethon import TelegramClient, sync


with open('config.json') as f:
    config = json.load(f)


API_ID = config['api_id']
API_HASH = config['api_hash']
CHAT_NAME = config['chat_name']
LIMIT = config['limit']
DATE = datetime.strptime(config['date'], '%d-%m-%Y %H:%M').date()
REVERSE = config["reverse"]
USERS = config["users"]


class Message:
    def __init__(self, id, user_id, text, reply_to):
        self.id = id
        self.user_id = user_id
        self.text = text
        self.reply_to = reply_to
        self.replies = []


def get_chat(chat_name):
    chats = client.get_dialogs()
    for cht in chats:
        if cht.name == chat_name:
            chat = cht
            return chat
    raise ValueError('Chat with this name does not exist')


def bfs(root):
    res = []
    q = deque([root])
    while q:
        for _ in range(len(q)):
            node = q.popleft()
            if node.id in marked:
                return None
            marked.add(node.id)
            res.append(node)
            for repl in node.replies:
                q.append(repl)
    return res

client = TelegramClient('session_name', API_ID, API_HASH)
client.start()

chat = get_chat(CHAT_NAME)
id_to_username = {i.id: i.username for i in client.get_participants(chat)}

messages = {}
for msg in client.iter_messages(chat, limit=LIMIT, offset_date=DATE, reverse=REVERSE):
    if not msg.text:
        continue
    messages[msg.id] = Message(msg.id, msg.from_id.user_id, msg.text, msg.reply_to_msg_id)

for i in messages:
    if not messages[i].reply_to:
        continue
    reply_to_msg = messages.get(messages[i].reply_to)
    if not reply_to_msg:
        continue
    reply_to_msg.replies.append(messages[i])

for username in USERS:
    with open(f"{username}.txt", 'w', encoding='utf-8') as f:
        marked = set()
        for msg in messages.values():
            tree = bfs(msg)
            if not tree or not any(id_to_username.get(msg.user_id) == username for msg in tree):
                continue
            for node in tree:
                f.write(f'message from {id_to_username.get(node.user_id, "unknown")}:\n')
                f.write(f'{node.text}\n')
                if node.reply_to:
                    reply_to_msg = messages.get(node.reply_to)
                    if not reply_to_msg:
                        continue
                    f.write(f'In replay to message from {id_to_username.get(reply_to_msg.user_id, "unknown")}:\n')
                    f.write(f'{reply_to_msg.text}\n')
                f.write('\n')
