import telebot
from telebot import types
from telebot.types import Message, CallbackQuery
import Config_data
from Keyboard.reply.contacts import city_markup
from Keyboard.reply.contacts import request_contact
from States.Contact_info import UserInfoState

from loader import bot

#bot = telebot.TeleBot(Config_data.config.token)


@bot.message_handler(content_types=['text'])
def start_message(message: Message) -> None:
    if message.text == '/start':
        bot.send_message(message.from_user.id, f'Hello {message.from_user.username}.\n'
                                               f'Could be glad help you.\n'
                                               f'Below you can find a commands which could direct you about hotels'
                                               f' to be choosed.'
                                               f' For other quations please push the button /help.')
        key_board = types.InlineKeyboardMarkup(row_width=1)
        lowprice = types.InlineKeyboardButton(text='/lowprice', callback_data='low-price_button_id')
        highprice = types.InlineKeyboardButton(text='/highprice', callback_data='high price_button_id')
        bestdeal = types.InlineKeyboardButton(text='/bestdeal', callback_data='best deal_button_id')
        history = types.InlineKeyboardButton(text='/history', callback_data='history_button_id')
        key_board.add(lowprice, highprice, bestdeal, history)
        bot.send_message(message.chat.id, 'Choose from menu', reply_markup=key_board)
    else:
        bot.send_message(message.from_user.id, f'/start - to begin work with chatbot.\n'
                                               f'/lowprice - To find cheapest hotels in the city.\n'
                                               f'/highprice - To find most expensive hotels in the city.\n'
                                               f'/bestdeal - To see the most suitable for the price and location from'
                                               f' the center.\n'
                                               f'/hystory - To view histories about hotels.')


@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    if callback.data == 'low-price_button_id':
        bot.send_message(callback.message.chat.id, 'In which city are you looking for a hotel?')
        bot.register_next_step_handler(callback.message, city_1)


def city_1(message: Message) -> None:
    res = city_markup(message.text)
    if res:
        bot.send_message(message.from_user.id, 'Please, clarify:',
                         reply_markup=res)  # Отправляем кнопки с вариантами


@bot.callback_query_handler(func=lambda call: callback.data.startswith('city_'))
def callback_cheking(callback: CallbackQuery) -> None:
    # call_data = '_'.join(call.data.split('_')[1:])
    callback.data = callback.data[6:]
    # if call.message:
    # call.data = call.data.strip('city_')
    if callback.data:
        bot.send_message(callback.message.chat.id, 'Good, your request is confirmed')
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text='some text',
                              reply_markup=None)
        bot.answer_callback_query(callback.id, text="Good, your request is confirmed, now how many hotels to show")
    # bot.reply_to(call.message, f'Отлично, твой запрос:')
    # bot.send_message(call.message.chat.id, 'Good, your request is confirmed')
    # bot.edit_message_text(call.message.chat.id, call.message.message_id, reply_markup=None)
    # logging.info(f'call={call.data}')
    # bot.send_message(call.message.chat.id, 'Good, your request is confirmed')


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == "yes":
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Загружаем фото")
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text="Не загружаем фото")


#   def low_price(message: Message) -> None:
#      name = message.text
#     UserInfoState.name = name
#    bot.send_message(message.from_user.id, f'{UserInfoState.name}, What city are you looking for an hotels?')


@bot.message_handler(content_types=['text'])
def start(message: Message) -> None:
    bot.send_message(message.chat.id, 'What is city are you looking for?')
    bot.register_next_step_handler(message, get_name)
    bot.set_state(message.from_user.id, UserInfoState.name)
    bot.send_message(message.from_user.id, 'Thanks, now enter your name')


@bot.message_handler(content_types='text', func=lambda message:
bot.get_state(message.from_user.id) == UserInfoState.name)
def get_name(message: Message) -> None:
    if message.text.isalpha() and message.text[0].isupper():
        name = message.text
        UserInfoState.name = name
        surname = message.text
        UserInfoState.surname = surname
        bot.register_next_step_handler(message, get_surname)
        bot.set_state(message.from_user.id, UserInfoState.surname)
        bot.send_message(message.from_user.id, 'Thanks, now enter your surname')
    else:
        bot.reply_to(message, 'The name starts with upper letter only')
        bot.set_state(message.from_user.id, UserInfoState.name)
        start(message)
        return


def get_surname(message: Message) -> None:
    if message.text.isalpha() and message.text[0].isupper():
        surname = message.text
        UserInfoState.name = surname
        bot.register_next_step_handler(message, get_age)
        bot.set_state(message.from_user.id, UserInfoState.age)
        bot.send_message(message.from_user.id, 'Thanks, now enter your age')
    else:
        bot.reply_to(message, 'The surname starts with upper letter only')
        bot.set_state(message.from_user.id, UserInfoState.surname)
        bot.register_next_step_handler(message, get_surname)
        return


def get_age(message: Message) -> None:
    if message.text.isdigit():
        age = message.text
        UserInfoState.age = age
        bot.register_next_step_handler(message, get_country)
        bot.set_state(message.from_user.id, UserInfoState.country)
        bot.send_message(message.from_user.id, 'Thanks, now enter your country')
    else:
        bot.reply_to(message, 'The age is number and contain digits')
        bot.set_state(message.from_user.id, UserInfoState.age)
        bot.register_next_step_handler(message, get_age)
        return


def get_country(message: Message) -> None:
    if message.text.isalpha() and message.text[0].isupper():
        country = message.text
        UserInfoState.country = country
        bot.register_next_step_handler(message, get_city)
        bot.set_state(message.from_user.id, UserInfoState.city)
        bot.send_message(message.from_user.id, 'Thanks, now enter your living city')
    else:
        bot.reply_to(message, 'The country starts with upper letter only')
        bot.set_state(message.from_user.id, UserInfoState.country)
        bot.register_next_step_handler(message, get_country)
        return


def get_city(message: Message) -> None:
    if message.text.isalpha() and message.text[0].isupper():
        city = message.text
        UserInfoState.city = city
        bot.register_next_step_handler(message, get_contact)
        bot.set_state(message.from_user.id, UserInfoState.cellphone)
        bot.send_message(message.from_user.id, 'Thanks, your turn enter cellphone number',
                         reply_markup=request_contact())
    else:
        bot.reply_to(message, 'The city starts with upper letter')
        bot.set_state(message.from_user.id, UserInfoState.city)
        bot.register_next_step_handler(message, get_city)
        return


@bot.message_handler(content_types=['text', 'contact'], state=UserInfoState.cellphone)
def get_contact(message: Message) -> None:
    if message.content_type == 'contact':
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cellphone'] = message.contact.phone_number
            text = 'thank you for accepted data: \n' \
                   'name - {}\n age {}\n country {}\n city {}\n cellphone number - {}'.format(
                data['name'], data['age'], data['country'], data['city'], data['cellphone'])
            bot.send_message(message.from_user.id, 'Excellent' + text)
    else:
        bot.send_message(message.from_user.id, 'To send please push the button')


bot.polling(none_stop=True, interval=2)