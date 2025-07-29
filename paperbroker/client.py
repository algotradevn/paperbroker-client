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
            username=username,
            log_dir=log_dir,
            console=console,
        )

    def connect(self):
        self.session.start()

    def disconnect(self):
        self.session.stop()

    # FIX
    def place_order(
        self,
        full_symbol,
        side,
        qty,
        price,
        ord_type="LIMIT",
        tif="GTC",
    ):
        return self.session.app.place_order(
            full_symbol=full_symbol,
            side=side,
            qty=qty,
            price=price,
            ord_type=ord_type,
            tif=tif,
        )

    def cancel_order(self, cl_ord_id):
        return self.session.app.cancel_order(cl_ord_id)

    def get_order_status(self, cl_ord_id):
        return self.session.app.get_order_status(cl_ord_id)

    def get_session_id(self):
        return self.session.app.get_session_id()

    # REST
    def get_remain_balance(self):
        return self.account_client.get_remain_balance()

    def get_stock_orders(self):
        return self.account_client.get_stock_orders()

    def get_derivative_orders(self):
        return self.account_client.get_derivative_orders()
