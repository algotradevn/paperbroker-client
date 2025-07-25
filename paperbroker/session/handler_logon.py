class LogonHandler:
    def __init__(self, logger):
        self.logger = logger

    def on_create(self, sessionID):
        self.logger.info(f"Session created: {sessionID}")

    def on_logon(self, sessionID):
        self.logger.info(f"Logon success: {sessionID}")

    def on_logout(self, sessionID):
        self.logger.info(f"Logged out: {sessionID}")
