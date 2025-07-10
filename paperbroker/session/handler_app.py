class AppHandler:
    def __init__(self, logger):
        self.logger = logger

    def to_app(self, message, sessionID):
        self.logger.debug(f"[TO APP] {message}")

    def from_app(self, message, sessionID):
        self.logger.info(f"[FROM APP] {message}")
