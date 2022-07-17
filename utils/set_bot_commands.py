from time import strftime

from telebot.types import BotCommand
from config_data.config import default_commands
import datetime


def set_default_commands(bot):
    bot.set_my_commands([BotCommand(*i) for i in default_commands])

