The telegram chatbot communicate with API server - "https://rapidapi.com" for parsing all datas related to travel
issues, like hotels searching and booking. For data storage has used library "peewee" as database to get search history
of various hotels and other.
Script for chatbot writing on python language version 3.9, using two main libraries:
1. pyTelegramBotAPI
2. Requests

A base structure of bot is followed:
1. "config.py";
2. "history_dataset.db";
3. "history_real.py";
4. "survey.py";
5. "contacts.py";
6. "contact_info.py";
7. "main.py".

Module "config.py" dedicated to config settings related to API keys, bot tokens.
File "history_dataset.db" created in order to collect search history of hotels.
Module "history_real.py" required for association with database, there are algorithm that proceed correct working of
database and flow.
Module "survey.py" dedicated for relationship between user's requests and chatbot output as answer to user.
Module "contacts.py" required for data parsing and working with API server.
Module "contact_info.py" required for saving intermedia data obtained from the users to the Class object and during
scenario retrieve it when take place.
Modul "main.py" required for data processing of chatbot.

In addition, ones virtual environment created, in order to work with chatbot also RAPID_API_KEY and BOT_TOKEN should be
introduced to local virtual environment file, marked as .env. A bot starts working ones you run "main.py" module on
python interface version 3.9 and highest.