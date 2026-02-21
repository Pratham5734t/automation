import logging
import requests

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


class TelegramNotifier:
    """Sends Telegram messages via the Bot API."""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def send(self, message: str) -> bool:
        """Send *message* to the configured Telegram chat.

        Returns True on success, False on failure.
        """
        if not self.token or not self.chat_id:
            logger.warning("Telegram not configured – skipping notification")
            return False

        url = TELEGRAM_API_URL.format(token=self.token)
        payload = {"chat_id": self.chat_id, "text": message}
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Telegram notification sent")
            return True
        except requests.RequestException as exc:
            logger.error("Failed to send Telegram notification: %s", exc)
            return False
