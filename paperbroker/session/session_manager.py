import quickfix as fix
from paperbroker.logger import get_logger
from .app import FIXApp


class FIXSessionManager:
    def __init__(
        self,
        cfg_path: str,
        account: str,
        username: str,
        password: str,
        log_dir: str = "logs",
    ):
        self.logger = get_logger("fixsession", log_dir)

        self.settings = fix.SessionSettings(cfg_path)
        self.store_factory = fix.FileStoreFactory(self.settings)

        self.app = FIXApp(
            account=account, username=username, password=password, logger=self.logger
        )

        self.initiator = fix.SocketInitiator(
            self.app, self.store_factory, self.settings
        )

    def start(self):
        self.logger.info("Starting FIX session...")
        self.initiator.start()

    def stop(self):
        self.logger.info("Stopping FIX session...")
        self.initiator.stop()
