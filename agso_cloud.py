import requests

from .const import BASE_URL


class AgsoCloud:
    def __init__(self, custno: int, subscription: int) -> None:
        self.custno = custno
        self.subscription = subscription
        self.token = None

    def authenticate(self, username: str, password: str) -> bool:
        req = requests.post(
            BASE_URL + "authenticate",
            json={"email": username, "password": password},
            timeout=5000,
        )

        if req.status_code != 200:
            return False

        resp = req.json()

        if "token" not in resp:
            return False

        self.token = resp["token"]
        return True
