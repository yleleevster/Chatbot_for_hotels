from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from Config_data import config

storage = StateMemoryStorage()
bot = TeleBot(token=config.token, state_storage=storage)
