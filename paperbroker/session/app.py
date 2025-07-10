import quickfix as fix
from paperbroker.logger import get_logger
from .handler_logon import LogonHandler
from .handler_admin import AdminHandler
from .handler_app import AppHandler


class FIXApp(fix.Application):  # ✅ MUST inherit this way
    def __init__(self, account: str, username: str, password: str, logger: str = None):
        super().__init__()  # ✅ Make sure C++ base initialized
        self.logger = logger or get_logger("fixapp")
        self.logon_handler = LogonHandler(logger=self.logger)
        self.admin_handler = AdminHandler(
            account=account, username=username, password=password, logger=self.logger
        )
        self.app_handler = AppHandler(logger=self.logger)

    def onCreate(self, sessionID):
        self.logon_handler.on_create(sessionID)

    def onLogon(self, sessionID):
        self.logon_handler.on_logon(sessionID)

    def onLogout(self, sessionID):
        self.logon_handler.on_logout(sessionID)

    def toAdmin(self, message, sessionID):
        self.admin_handler.to_admin(message, sessionID)

    def fromAdmin(self, message, sessionID):
        self.admin_handler.from_admin(message, sessionID)

    def toApp(self, message, sessionID):
        self.app_handler.to_app(message, sessionID)

    def fromApp(self, message, sessionID):
        self.app_handler.from_app(message, sessionID)
