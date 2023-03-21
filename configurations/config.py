import logging

from aiogram import types
from decouple import config
from handlers.commands import register as reg_commands
from handlers.registration import register as reg_registr
from handlers.searching import register as reg_searching
from handlers.subscription import register as reg_subscription
from handlers.favorite import register as reg_favorite
from handlers.feedback import register as reg_feedback


bot_token = config("BOT_TOKEN")
logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot")
    ])


def register_handlers(dp):
    reg_commands(dp)
    reg_registr(dp)
    reg_searching(dp)
    reg_subscription(dp)
    reg_favorite(dp)
    reg_feedback(dp)
