import httpx


class TelegramClient:
    def __init__(
        self,
        bot_token: str = "",
        chat_id: str = "",
        timeout_seconds: int = 10,
        http_client=None,
    ) -> None:
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.timeout_seconds = timeout_seconds
        self.http_client = http_client

    def is_configured(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_message(self, message: str, dry_run: bool = True) -> dict:
        if not self.is_configured():
            return {
                "sent": False,
                "skipped": True,
                "dry_run": dry_run,
                "reason": "telegram token or chat id missing",
                "message": message,
            }

        if dry_run:
            return {
                "sent": False,
                "skipped": False,
                "dry_run": True,
                "reason": "dry run",
                "message": message,
            }

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "disable_web_page_preview": True,
        }

        try:
            if self.http_client is not None:
                response = self.http_client.post(url, json=payload, timeout=self.timeout_seconds)
            else:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return {
                "sent": False,
                "skipped": False,
                "dry_run": False,
                "reason": "telegram send failed",
                "error": str(exc),
                "message": message,
            }

        return {
            "sent": True,
            "skipped": False,
            "dry_run": False,
            "reason": None,
            "message": message,
        }
