from paperbroker.rest.rest_session import RestSession


class AccountClient:
    def __init__(self, rest_session: "RestSession"):
        self.rest = rest_session

    def get_account_info(self, account_id: str):
        return self.rest.post("/api/account/info", {"accountID": account_id})
