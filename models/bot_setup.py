import asyncio, os, logging
from aiogram import Bot, Dispatcher
from .handlers import router


def start_bot():
    token = os.getenv("BOT_TOKEN")
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(dp.start_polling(bot, handle_signals=False))