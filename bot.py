from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
import configurations.config as cfg
import asyncio
import logging


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'[%(asctime)s] - %(message)s')
    cfg.logger.info("Starting bot")

    bot = Bot(cfg.bot_token, parse_mode=types.ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)
    cfg.register_handlers(dp)

    await cfg.set_default_commands(dp)
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
