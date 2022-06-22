import os
import sqlite3
from dotenv import load_dotenv, find_dotenv
import telebot
from telebot.storage import StateMemoryStorage
if not find_dotenv():
    print('The variable of environment has not downloaded so file .env not found')
else:
    load_dotenv()


token = os.getenv('BOT_TOKEN')
rapid_api_key = os.getenv('RAPID_API_KEY')
default_commands = (('Start', 'Lets go'), ('Help', 'Go out information'), ('Survey', 'Get data'))
state_storage = StateMemoryStorage()
bot = telebot.TeleBot(token, state_storage=state_storage)
data_base = 'collecttable.db'
#os.environ['TOKEN'] = '5309243154:AAGvxre4wxJJ3B_nPUv992ruCRllOnCGfAA'
#os.environ['rapid_api_key'] = 'secret'