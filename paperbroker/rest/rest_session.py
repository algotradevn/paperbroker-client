import requests


class RestSession:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def post(self, path: str, json: dict):
        url = f"{self.base_url}{path}"
        response = requests.post(url, json=json)
        response.raise_for_status()
        return response.json()

    def get(self, path: str, params: dict = None):
        url = f"{self.base_url}{path}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
