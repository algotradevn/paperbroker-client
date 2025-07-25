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
                    extra={"username": self.username, "response": str(response)},
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

    def get_account_info(self) -> dict:
        if not self._ensure_account_id():
            self.logger.warning(
                "event=account_info_skipped_due_to_missing_id",
                extra={"username": self.username},
            )
            return {}

        try:
            response = self.rest.post(
                "/api/account/info",
                {"accountID": self.ID},
            )
            if not isinstance(response, dict):
                self.logger.warning(
                    "event=account_info_invalid_format",
                    extra={"accountID": self.ID, "response": str(response)},
                )
                return {}
            return response
        except Exception as e:
            self.logger.error(
                "event=account_info_fetch_failed",
                extra={"accountID": self.ID, "error": str(e)},
            )
            return {}
