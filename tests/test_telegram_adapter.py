import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from src.api.main import app
from src.adapters.telegram_adapter import TelegramClient, parse_telegram_update

client = TestClient(app)

def test_parse_telegram_update_valid_payload():
    payload = {
        "update_id": 1001,
        "message": {
            "message_id": 42,
            "from": {"id": 12345, "first_name": "Paulo"},
            "chat": {"id": 12345, "type": "private"},
            "text": "Olá Nura!"
        }
    }
    update = parse_telegram_update(payload)
    assert update is not None
    assert update.update_id == 1001
    assert update.message.chat_id == 12345
    assert update.message.text == "Olá Nura!"

def test_parse_telegram_update_invalid_or_non_text_payload():
    payload = {"update_id": 1002}
    update = parse_telegram_update(payload)
    assert update is not None
    assert update.message is None

def test_telegram_client_send_message_mocked():
    mock_http = MagicMock()
    mock_http.post.return_value.json.return_value = {"ok": True, "result": {"message_id": 43}}
    mock_http.post.return_value.status_code = 200

    tg_client = TelegramClient(bot_token="TEST_BOT_TOKEN", http_session=mock_http)
    res = tg_client.send_message(chat_id=12345, text="Refeição confirmada!", reply_markup={"inline_keyboard": []})

    assert res["ok"] is True
    assert mock_http.post.call_count == 1
    call_args = mock_http.post.call_args
    assert "https://api.telegram.org/botTEST_BOT_TOKEN/sendMessage" in call_args[0][0]
    assert call_args[1]["json"]["chat_id"] == 12345
    assert call_args[1]["json"]["text"] == "Refeição confirmada!"

def test_webhook_telegram_endpoint_post():
    payload = {
        "update_id": 1003,
        "message": {
            "message_id": 44,
            "from": {"id": 999, "first_name": "Ana"},
            "chat": {"id": 999, "type": "private"},
            "text": "Confirmar almoço"
        }
    }
    response = client.post("/webhook/telegram", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
