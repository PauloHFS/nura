import requests
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class TelegramMessage:
    message_id: int
    chat_id: int
    user_id: int
    text: str

@dataclass
class TelegramUpdate:
    update_id: int
    message: Optional[TelegramMessage] = None

def parse_telegram_update(payload: Dict[str, Any]) -> TelegramUpdate:
    """Extrai e valida dados de mensagem de um payload do Telegram Bot API."""
    update_id = payload.get("update_id", 0)
    msg_data = payload.get("message")

    if not msg_data or not isinstance(msg_data, dict):
        return TelegramUpdate(update_id=update_id, message=None)

    chat = msg_data.get("chat", {})
    from_user = msg_data.get("from", {})
    text = msg_data.get("text", "")

    msg = TelegramMessage(
        message_id=msg_data.get("message_id", 0),
        chat_id=chat.get("id", 0),
        user_id=from_user.get("id", 0),
        text=text,
    )
    return TelegramUpdate(update_id=update_id, message=msg)

class TelegramClient:
    """Cliente HTTP para envio de mensagens proativas e teclados interativos no Telegram."""

    def __init__(self, bot_token: str, http_session: Optional[Any] = None):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = http_session or requests.Session()

    def send_message(
        self,
        chat_id: int,
        text: str,
        reply_markup: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        if hasattr(self.session, "post"):
            res = self.session.post(url, json=payload, timeout=10)
            if hasattr(res, "json"):
                return res.json()
            return {"ok": True}
        return {"ok": True}
