import requests
from typing import Iterable, Optional, Union

from django.conf import settings


TELEGRAM_BOT_TOKEN: Optional[str] = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
TELEGRAM_CHAT_ID: Optional[Union[int, str]] = getattr(settings, "TELEGRAM_CHAT_ID", None)
TELEGRAM_ADMINS: Iterable[Union[int, str]] = getattr(settings, "TELEGRAM_ADMINS", ())

API_BASE_URL: Optional[str] = (
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}" if TELEGRAM_BOT_TOKEN else None
)


def _send_message(chat_id: Union[int, str], text: str) -> bool:
    """
    Базовая отправка сообщения в Telegram.
    """
    if not TELEGRAM_BOT_TOKEN or not API_BASE_URL:
        return False

    try:
        response = requests.post(
            f"{API_BASE_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=5,
        )
        return response.ok
    except Exception:
        # Логи можно дописать при необходимости
        return False


def _broadcast(text: str) -> None:
    """
    Отправка сообщения только в канал (CHAT_ID).
    """
    if TELEGRAM_CHAT_ID:
        _send_message(TELEGRAM_CHAT_ID, text)


def _format_request_block(
    kind: str,
    name: str,
    phone: str,
    contact_method: Optional[str],
    contact_value: str,
    comment: Optional[str],
) -> str:
    """
    Единый формат для "Заявка" и "Консультация".

    Поля строго по ТЗ:
    - Консультация/Заявка
    - имя
    - номер
    - telegram/VK (user/ссылка)
    - комментарий
    """
    lines = [
        f"🆕 <b>{kind}</b>",
        "",
        f"Имя: <b>{name}</b>",
        f"Номер: <b>{phone}</b>",
    ]

    method_label = (contact_method or "").upper() if contact_method else ""
    if contact_value:
        if method_label:
            lines.append(f"Контакт: <b>{contact_value}</b> ({method_label})")
        else:
            lines.append(f"Контакт: <b>{contact_value}</b>")

    if comment:
        lines.append("")
        lines.append(f"Комментарий:\n{comment}")

    return "\n".join(lines)


def notify_new_lead(
    *,
    name: str,
    phone: str,
    contact_method: Optional[str],
    contact_value: str,
    comment: Optional[str],
) -> None:
    """
    Уведомление о новой ЗАЯВКЕ с сайта.
    """
    if not TELEGRAM_CHAT_ID:
        return

    text = _format_request_block(
        kind="Заявка",
        name=name,
        phone=phone,
        contact_method=contact_method,
        contact_value=contact_value,
        comment=comment,
    )
    _broadcast(text)


def notify_new_consultation(
    *,
    name: str,
    phone: str,
    contact_method: Optional[str],
    contact_value: str,
    comment: Optional[str],
) -> None:
    """
    Уведомление о новой КОНСУЛЬТАЦИИ.
    """
    if not TELEGRAM_CHAT_ID:
        return

    text = _format_request_block(
        kind="Консультация",
        name=name,
        phone=phone,
        contact_method=contact_method,
        contact_value=contact_value,
        comment=comment,
    )
    _broadcast(text)

