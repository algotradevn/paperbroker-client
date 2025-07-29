from paperbroker.rest.rest_session import RestSession
from paperbroker.logger import get_logger


class AccountClient:
    def __init__(
        self,
        rest_session: "RestSession",
        username: str,
        log_dir: str = "logs",
        console: bool = False,
    ):
        self.rest = rest_session
        self.username = username
        self.logger = get_logger(log_dir, console)
        self.ID = None  # Will be resolved lazily

    def _fetch_account_id(self) -> str | None:
        try:
            response = self.rest.get(
                "/api/account/by-username",
                params={"username": self.username},
            )
            if isinstance(response, dict) and "accountID" in response:
                self.logger.info(
                    "event=account_id_resolved",
                    extra={
                        "username": self.username,
                        "accountID": response["accountID"],
                    },
                )
                return response["accountID"]
            else:
                self.logger.warning(
                    "event=account_id_fetch_invalid",
                    extra={
                        "username": self.username,
                        "response": str(response),
                    },
                )
        except Exception as e:
            self.logger.error(
                "event=account_id_fetch_failed",
                extra={"username": self.username, "error": str(e)},
            )
        return None

    def _ensure_account_id(self) -> bool:
        if self.ID is None:
            self.ID = self._fetch_account_id()
        return self.ID is not None

    def get_remain_balance(self) -> dict:
        """Fetch remain balance for the current account."""
        if not self._ensure_account_id():
            self.logger.warning(
                "event=remain_balance_skipped_due_to_missing_id",
                extra={"username": self.username},
            )
            return {}

        try:
            response = self.rest.get(
                "/api/account/remain-balance",
                params={"accountID": self.ID},
            )
            if isinstance(response, dict) and "remainBalance" in response:
                self.logger.info(
                    "event=remain_balance_resolved",
                    extra={
                        "accountID": response.get("accountID", self.ID),
                        "remainBalance": str(response["remainBalance"]),
                    },
                )
                return {
                    "accountID": response.get("accountID", self.ID),
                    "remainBalance": response["remainBalance"],
                }
            else:
                self.logger.warning(
                    "event=remain_balance_invalid_format",
                    extra={"accountID": self.ID, "response": str(response)},
                )
                return {}
        except Exception as e:
            self.logger.error(
                "event=remain_balance_fetch_failed",
                extra={"accountID": self.ID, "error": str(e)},
            )
            return {}

    def get_stock_orders(self) -> list[dict]:
        """Fetch stock orders for the current account."""
        if not self._ensure_account_id():
            self.logger.warning(
                "event=stock_orders_skipped_due_to_missing_id",
                extra={"username": self.username},
            )
            return []

        try:
            response = self.rest.get(
                "/api/account/orders/stock",
                params={"accountID": self.ID},
            )
            if isinstance(response, list):
                self.logger.info(
                    "event=stock_orders_resolved",
                    extra={"accountID": self.ID, "count": len(response)},
                )
                return response
            else:
                self.logger.warning(
                    "event=stock_orders_invalid_format",
                    extra={"accountID": self.ID, "response": str(response)},
                )
                return []
        except Exception as e:
            self.logger.error(
                "event=stock_orders_fetch_failed",
                extra={"accountID": self.ID, "error": str(e)},
            )
            return []

    def get_derivative_orders(self) -> list[dict]:
        """Fetch derivative orders for the current account."""
        if not self._ensure_account_id():
            self.logger.warning(
                "event=derivative_orders_skipped_due_to_missing_id",
                extra={"username": self.username},
            )
            return []

        try:
            response = self.rest.get(
                "/api/account/orders/derivative",
                params={"accountID": self.ID},
            )
            if isinstance(response, list):
                self.logger.info(
                    "event=derivative_orders_resolved",
                    extra={"accountID": self.ID, "count": len(response)},
                )
                return response
            else:
                self.logger.warning(
                    "event=derivative_orders_invalid_format",
                    extra={"accountID": self.ID, "response": str(response)},
                )
                return []
        except Exception as e:
            self.logger.error(
                "event=derivative_orders_fetch_failed",
                extra={"accountID": self.ID, "error": str(e)},
            )
            return []
