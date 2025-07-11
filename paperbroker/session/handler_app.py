import quickfix as fix


class AppHandler:
    def __init__(self, account, username, password, logger):
        self.account = account
        self.username = username
        self.password = password
        self.logger = logger

    def to_app(self, message, sessionID):
        message.setField(fix.Username(self.username))
        message.setField(fix.Account(self.account))
        self.logger.debug(f"[TO APP] {message}")

    def from_app(self, message, sessionID):
        self.logger.info(f"[FROM APP] {message}")
