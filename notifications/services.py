import asyncio
import logging
import os
from decimal import Decimal
from typing import Iterable, List, Tuple

from django.utils.timezone import now

from borrowings.models import Borrowing
from payments.models import Payment

logger = logging.getLogger(__name__)


def _get_admin_chat_ids() -> List[int]:
    raw = os.getenv("TELEGRAM_ADMINS_CHAT_IDS") or os.getenv(
        "TELEGRAM_ADMINS_CHAT_ID"
    )
    if not raw:
        logger.warning(
            "TELEGRAM_ADMINS_CHAT_IDS is not set; skipping notifications"
        )
        return []
    ids: List[int] = []
    for part in str(raw).split(","):
        part = part.strip()
        if not part:
            continue
        try:
            ids.append(int(part))
        except ValueError:
            # skip invalid entries silently
            continue
    return ids


def _build_bot():
    from aiogram import Bot  # local import to avoid hard dependency at import-time
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set in environment"
        )
    return Bot(token=token)


def _sync_send_messages(chat_ids: Iterable[int], text: str, *, parse_mode: str | None = "HTML") -> None:
    async def _send():
        bot = _build_bot()
        try:
            for chat_id in chat_ids:
                try:
                    await bot.send_message(chat_id, text, parse_mode=parse_mode, disable_web_page_preview=True)
                except Exception as e:
                    logger.warning("Telegram send failed for chat %s: %r", chat_id, e)
                    continue
        finally:
            await bot.session.close()

    asyncio.run(_send())


_CURRENCY_SIGNS = {"USD": "$", "EUR": "€", "UAH": "₴", "GBP": "£"}


def _fmt_money(amount: Decimal, currency: str | None) -> str:
    code = (currency or "USD").upper()
    sign = _CURRENCY_SIGNS.get(code, "")
    return f"{sign}{amount:.2f} {code}"


def notify_payment_success_admin(payment_id: int, currency: str | None = None) -> None:
    payment = Payment.objects.select_related(
        "borrowing", "borrowing__book", "borrowing__user"
    ).get(id=payment_id)

    if payment.status != Payment.Status.paid:
        return

    user_label = getattr(payment.borrowing.user, "email", payment.borrowing.user_id)
    amount_str = _fmt_money(payment.money_to_pay, currency)

    text = (
        "✅ <b>Payment received</b>\n\n"
        f"💳 <b>Type:</b> <code>{payment.type}</code>\n"
        f"💰 <b>Amount:</b> <b>{amount_str}</b>\n"
        f"📘 <b>Book:</b> {payment.borrowing.book.title}\n"
        f"👤 <b>User:</b> {user_label}\n"
        f"📅 <b>Borrowed:</b> {payment.borrowing.borrow_date}\n"
        f"⏳ <b>Expected return:</b> {payment.borrowing.expected_return_date}"
    )

    admin_ids = _get_admin_chat_ids()
    if admin_ids:
        _sync_send_messages(admin_ids, text)
    else:
        logger.info(
            "No admin chat IDs configured; skipping payment notification for id=%s",
            payment_id,
        )


def build_overdue_summary() -> Tuple[int, str]:
    """
    Повертає (кількість, текст) без надсилання в Telegram.
    Текст уже відформатований під parse_mode="HTML".
    """
    today = now().date()
    overdue = Borrowing.objects.select_related("book", "user").filter(
        expected_return_date__lt=today,
        actual_return_date__isnull=True
    )
    count = overdue.count()

    if count == 0:
        return 0, "✅ <b>No overdue borrowings today</b>"

    lines = [f"⚠️ <b>Overdue borrowings ({count})</b>:\n"]
    for b in overdue[:20]:
        user_label = getattr(b.user, "email", b.user_id)
        lines.append(
            f"• 📚 <b>{b.book.title}</b> — 👤 {user_label} "
            f"(⏳ due <b>{b.expected_return_date}</b>)"
        )

    if count > 20:
        lines.append(f"… and <b>{count - 20}</b> more")

    return count, "\n".join(lines)


def notify_overdue_borrowings_admin() -> int:
    count, text = build_overdue_summary()
    admin_ids = _get_admin_chat_ids()
    if not admin_ids:
        logger.info("No admin chat IDs configured; skipping overdue summary")
        return count
    _sync_send_messages(admin_ids, text)
    return count
