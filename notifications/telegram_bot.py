import os
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from asgiref.sync import sync_to_async

from .services import build_overdue_summary


def _get_token() -> str:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is not set in environment"
        )
    return token


def build_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=_get_token())
    dp = Dispatcher()

    @dp.message(CommandStart())  # заміна F.text == "/start"
    async def cmd_start(message: Message):
        await message.answer("Library Notifications Bot online. Commands: /overdue")

    @dp.message(Command("overdue"))  # заміна F.text == "/overdue"
    async def cmd_overdue(message: Message):
        _, text = await sync_to_async(build_overdue_summary, thread_sensitive=True)()
        await message.answer(text, parse_mode="HTML")

    return bot, dp


async def run_polling() -> None:
    bot, dp = build_bot_and_dispatcher()
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def run():
    asyncio.run(run_polling())
