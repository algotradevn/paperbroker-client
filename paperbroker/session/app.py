import quickfix as fix
from typing import Optional
from paperbroker.logger import get_logger
from .OrderManager import OrderManager
from .handler_logon import LogonHandler
from .handler_admin import AdminHandler
from .handler_app import AppHandler


class FIXApp(fix.Application):
    def __init__(
        self,
        account: str,
        username: str,
        password: str,
        logger: Optional[str] = None,
        console: bool = False,
    ):
        super().__init__()
        self.logger = logger or get_logger(console=console)

        # Handlers
        self.logon_handler = LogonHandler(logger=self.logger)
        self.admin_handler = AdminHandler(
            account=account,
            username=username,
            password=password,
            logger=self.logger,
        )
        self.app_handler = AppHandler(
            account=account,
            username=username,
            password=password,
            logger=self.logger,
        )

        # Order manager
        self.order_manager = OrderManager(logger=self.logger)

        # FIX session ID
        self.session_id = None

    def onCreate(self, sessionID):
        self.logon_handler.on_create(sessionID)

    def onLogon(self, sessionID):
        self.session_id = sessionID
        self.logon_handler.on_logon(sessionID)
        self.order_manager.set_session(sessionID)

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
        self.order_manager.on_execution_report(message)

    def place_order(
        self,
        full_symbol,
        side,
        qty,
        price,
        ord_type="LIMIT",
        tif="GTC",
    ):
        return self.order_manager.place_order(
            full_symbol=full_symbol,
            side=side,
            qty=qty,
            price=price,
            ord_type=ord_type,
            tif=tif,
        )

    def cancel_order(self, cl_ord_id):
        return self.order_manager.cancel_order(cl_ord_id)

    def get_order_status(self, cl_ord_id):
        return self.order_manager.get_order_status(cl_ord_id)

    def get_session_id(self):
        return self.session_id if self.session_id else None
