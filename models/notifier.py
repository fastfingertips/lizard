import requests
import json

class Notifier:

    link = "https://ntfy.sh/"
    encoding = 'utf-8'

    def __init__(self):
        pass

    @classmethod
    def link_update(cls, code):
        raw = f'https://rentry.co/{code}/raw'
        data = requests.get(raw)
        cls.link += json.loads(data.content)['log_id']

    def send(self, message, link=None):
        requests.post(
            link if link else self.link,
            data=str(message).encode(encoding=self.encoding)
            )