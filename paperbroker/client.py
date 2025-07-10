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
