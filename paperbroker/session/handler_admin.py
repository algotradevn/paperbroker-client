import quickfix as fix


class AdminHandler:
    def __init__(self, account, username, password, logger):
        self.account = account
        self.username = username
        self.password = password
        self.logger = logger

    def to_admin(self, message, sessionID):
        msg_type = message.getHeader().getField(fix.MsgType()).getString()
        if msg_type == "A":  # Logon
            message.setField(fix.Account(self.account))
            message.setField(fix.Username(self.username))
            message.setField(fix.Password(self.password))
            message.setField(fix.EncryptMethod(0))
            message.setField(fix.HeartBtInt(30))
        self.logger.debug(f"[TO ADMIN] {message}")

    def from_admin(self, message, sessionID):
        self.logger.debug(f"[FROM ADMIN] {message}")
