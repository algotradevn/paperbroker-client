from paperbroker.rest.rest_session import RestSession
from paperbroker.logger import get_logger


class AccountClient:
    def __init__(
        self,
        rest_session: "RestSession",
        log_dir: str = "logs",
        console: bool = False,
    ):
        self.rest = rest_session
        self.logger = get_logger(log_dir, console)

    def get_account_info(self, account_id: str) -> dict:
        try:
            response = self.rest.post(
                "/api/account/info",
                {"accountID": account_id},
            )
            if not isinstance(response, dict):
                self.logger.warning(
                    "event=account_info_invalid_format",
                    extra={"accountID": account_id, "response": str(response)},
                )
                return {}
            return response
        except Exception as e:
            self.logger.error(
                "event=account_info_fetch_failed",
                extra={"accountID": account_id, "error": str(e)},
            )
            return {}
