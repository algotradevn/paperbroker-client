from paperbroker.rest.rest_session import RestSession
from paperbroker.rest.account_client import AccountClient
from paperbroker.session.session_manager import FIXSessionManager


class PaperBrokerClient:
    def __init__(
        self,
        account: str,
        username: str,
        password: str,
        cfg_path: str,
        log_dir: str = "logs",
        rest_base_url: str = "http://localhost:8000",
        console: bool = False,
    ):
        self.session = FIXSessionManager(
            cfg_path=cfg_path,
            account=account,
            username=username,
            password=password,
            log_dir=log_dir,
            console=console,
        )

        # REST clients
        self.rest_session = RestSession(rest_base_url)
        self.account_client = AccountClient(
            rest_session=self.rest_session,
            log_dir=log_dir,
            console=console,
        )

    def connect(self):
        self.session.start()

    def disconnect(self):
        self.session.stop()

    # FIX
    def place_order(self, symbol, side, qty, price, ord_type="LIMIT", tif="GTC"):
        return self.session.app.place_order(symbol, side, qty, price, ord_type, tif)

    def cancel_order(self, cl_ord_id):
        return self.session.app.cancel_order(cl_ord_id)

    def get_order_status(self, cl_ord_id):
        return self.session.app.get_order_status(cl_ord_id)

    def get_session_id(self):
        return self.session.app.get_session_id()

    # REST
    def get_account_info(self, account_id: str):
        return self.account_client.get_account_info(account_id)
