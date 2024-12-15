import requests
import json

class Notifier:

    link = "https://ntfy.sh/"
    encoding = 'utf-8'

    def __init__(self):
        pass

    @classmethod
    def set_link_code(cls, code):
        cls.link += code

    def get_link_code_from_rentry(cls, code, key="log_id"):
        raw = f'https://rentry.co/{code}/raw'
        data = requests.get(raw)
        return json.loads(data.content)[key]

    def send(self, message, link=None):
        requests.post(
            link if link else self.link,
            data=str(message).encode(encoding=self.encoding)
            )