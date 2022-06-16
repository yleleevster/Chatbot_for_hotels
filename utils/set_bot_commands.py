from telebot.types import BotCommand
from Config_data.config import default_commands
#from loader import bot


def set_default_commands(bot):
    bot.set_my_commands([BotCommand(*i) for i in default_commands])


