from datetime import datetime
from collections import deque
import json


with open('config.json') as f:
    config = json.load(f)

START_DATE = datetime.strptime(config['start_date'], '%Y-%m-%d %H:%M')
END_DATE = datetime.strptime(config['end_date'], '%Y-%m-%d %H:%M')
USERS = config["users"]


class Message:
    def __init__(self, id, from_user, text, reply_to):
        self.id = id
        self.from_user = from_user
        self.text = text
        self.reply_to = reply_to
        self.replies = []


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


with open('result.json') as f:
    chat = json.load(f)


messages = {}
for msg in chat['messages']:
    if msg['type'] != 'message' or not msg['text']:
        continue
    date = datetime.strptime(msg['date'], '%Y-%m-%dT%H:%M:%S')
    if date < START_DATE or date > END_DATE:
        continue
    messages[msg['id']] = Message(id=msg['id'],
                                  from_user=msg['from'],
                                  text=' '.join(i['text'] for i in msg['text_entities']),
                                  reply_to=msg.get('reply_to_message_id'))


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
            if not tree or not any(msg.from_user == username for msg in tree):
                continue
            for node in tree:
                f.write(f'message from {node.from_user}:\n')
                f.write(f'{node.text}\n')
                if node.reply_to:
                    reply_to_msg = messages.get(node.reply_to)
                    if not reply_to_msg:
                        continue
                    f.write(f'In replay to message from {reply_to_msg.from_user}:\n')
                    f.write(f'{reply_to_msg.text}\n')
                f.write('\n')
