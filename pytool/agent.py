from typing import Dict
import requests


URL = "http://127.0.0.1:3334/LocalTest"


class JavaAgent:

    def __init__(self, url: str = None, timeout: int = 60) -> None:
        self.url = url or URL
        self.timeout = timeout

    def debug(self, **kvargs) -> Dict:
        r = requests.get(self.url, data=kvargs, timeout=self.timeout)
        try:
            return r.json()
        except:
            return {'code': 404, 'message': r.text}
