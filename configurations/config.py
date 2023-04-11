import logging

from aiogram import types
from decouple import config
from handlers.commands import register as reg_commands
from handlers.registration import register as reg_registration
from handlers.searching import register as reg_searching
from handlers.subscription import register as reg_subscription
from handlers.favorite import register as reg_favorite
from handlers.feedback import register as reg_feedback
from handlers.request import register as reg_request

bot_token = config("BOT_TOKEN")
logger = logging.getLogger(__name__)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Start bot"),
        types.BotCommand("find", "Find apartments"),
        types.BotCommand("favorites", "Show favorites"),
        # types.BotCommand("profile", "Edit profile"),
        types.BotCommand("language", "Edit language"),
        types.BotCommand("request", "Last saved request"),
        types.BotCommand("feedback", "Send feedback")
    ])


def register_handlers(dp):
    reg_commands(dp)
    reg_registration(dp)
    reg_searching(dp)
    reg_subscription(dp)
    reg_favorite(dp)
    reg_feedback(dp)
    reg_request(dp)
