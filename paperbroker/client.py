from paperbroker.session.session_manager import FIXSessionManager


class PaperBrokerClient:
    def __init__(
        self,
        account: str,
        username: str,
        password: str,
        cfg_path: str,
        log_dir: str = "logs",
    ):
        self.session = FIXSessionManager(
            cfg_path=cfg_path,
            account=account,
            username=username,
            password=password,
            log_dir=log_dir,
        )

    def connect(self):
        self.session.start()

    def disconnect(self):
        self.session.stop()

    def place_order(self, symbol, side, qty, price, ord_type="LIMIT", tif="GTC"):
        return self.session.app.place_order(symbol, side, qty, price, ord_type, tif)

    def cancel_order(self, cl_ord_id):
        return self.session.app.cancel_order(cl_ord_id)

    def get_order_status(self, cl_ord_id):
        return self.session.app.get_order_status(cl_ord_id)

    def get_session_id(self):
        return self.session.app.get_session_id()
