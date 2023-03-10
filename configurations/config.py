import logging

from aiogram import types
from decouple import config
from handlers.commands import register as reg_commands

bot_token = config("BOT_TOKEN")
logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot")
    ])


def register_handlers(dp):
    reg_commands(dp)
