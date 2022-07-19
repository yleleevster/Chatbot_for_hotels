import os
from dotenv import load_dotenv, find_dotenv
import telebot
from telebot.storage import StateMemoryStorage
if not find_dotenv():
    print('The variable of environment has not downloaded so file .env not found')
else:
    load_dotenv()

token = os.getenv('BOT_TOKEN')
rapid_api_key = os.getenv('RAPID_API_KEY')
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token, state_storage=state_storage)
