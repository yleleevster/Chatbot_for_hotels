import datetime
import json
from time import strftime
from loguru import logger
import sqlite3 as sq
from telebot import types, util
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import WYearTelegramCalendar, LSTEP

import config_data
from config_data.config import bot
from database import write_check_date
from keyboard.reply.contacts import city_markup, gen_markup, hotel_suggestions, \
    hotel_suggestions_highest, hotel_markup, photos, request_contact, request_city_markup, best_seller
from states.contact_info import max_hotel_counter, max_image_counter, UserInfoState, Users

data_set = dict()


# data_set[call.message.chat.id] = dict()


class MyStyleCalendar(WYearTelegramCalendar):
    """ Class for custom style of representation """
    prev_button = "⬅️"
    next_button = "➡️"
    empty_month_button = ""
    empty_year_button = ""


@bot.message_handler(content_types=['text'])
def start_message(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.command = message.text
    if user.command.lower() == '/start' or user.command.lower() == '/hello-world' or user.command.lower() == 'привет':
        bot.send_message(user.user_id, f'Hello {user.user_id}.\n'
                                       f'Could be glad help you.\n'
                                       f'Below you can find a commands which could direct you about hotels'
                                       f' to be chosen.'
                                       f' For other quations please push the button /help.')
        key_board = types.InlineKeyboardMarkup(row_width=1)
        lowprice = types.InlineKeyboardButton(text='/lowprice', callback_data='low-price_button_id')
        highprice = types.InlineKeyboardButton(text='/highprice', callback_data='high price_button_id')
        bestdeal = types.InlineKeyboardButton(text='/bestdeal', callback_data='best deal_button_id')
        history = types.InlineKeyboardButton(text='/history', callback_data='history_button_id')
        key_board.add(lowprice, highprice, bestdeal, history)
        bot.send_message(message.chat.id, 'Choose from menu', reply_markup=key_board)
    else:
        bot.send_message(user.user_id, f'/start, /hello-world, /привет - to begin work with chatbot.\n'
                                       f'/lowprice - To find cheapest hotels in the city.\n'
                                       f'/highprice - To find most expensive hotels in the city.\n'
                                       f'/bestdeal - To see the most suitable for the price and location from'
                                       f' the center.\n'
                                       f'/hystory - To view histories about hotels.')


@bot.callback_query_handler(func=lambda callback: callback.data == 'low-price_button_id')
def check_callback_data_1(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    #user.all_users.get(user.command)
    bot.send_message(user.user_id, 'In which city are you looking for a hotel?')
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, request_city)


@bot.callback_query_handler(func=lambda callback: callback.data == 'high price_button_id')
def check_callback_data_2(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    bot.send_message(user.user_id, 'In which city are you looking for a hotel?')
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, request_city)


@bot.callback_query_handler(func=lambda callback: callback.data == 'best deal_button_id')
def check_callback_data_3(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    # callback_obj.data = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    print(user.datetime)
    bot.send_message(user.user_id, 'In which city are you looking for a hotel?')
    # bot.set_state(callback_obj.from_user.id, UserInfoState.city, callback_obj.message.message_id)
    # with bot.retrieve_data(callback_obj.from_user.id, callback_obj.id) as data:
    # data['command'] = callback_obj.data
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, request_city)


def request_city(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.city = message.text
    collect_data = request_city_markup(user)
    if collect_data:
        bot.send_message(user.user_id, 'Fine, you have chosen {}, please clarify:'.format(user.city),
                         reply_markup=collect_data)  # Отправляем кнопки с вариантами
        # bot.set_state(message.from_user.id, UserInfoState.district, message.chat.id)
        # else:
        # bot.send_message(message.chat.id, 'Please try again')
        # bot.register_next_step_handler(message, callback_cheking)


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def callback_validation(callback_obj: CallbackQuery) -> None:
    user = Users.get_user(callback_obj.from_user.id)
    destination_id = callback_obj.data[5:]
    user.destinationId = destination_id
    # user_id = callback_obj.from_user.id
    if not callback_obj.data.isalpha():
        bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
                              text=f'Good, your request is confirmed - {user.destinationId}')
        # with bot.retrieve_data(callback_obj.from_user.id, callback_obj.message.chat.id) as data:
        # data['destinationID'] = callback_obj.data
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute(""" DROP TABLE IF EXISTS best_deal_results""")
        # cur.execute(""" CREATE TABLE IF NOT EXISTS best_deal_results(
        # user_id INTEGER PRIMARY KEY autoincrement,
        # destinationID TEXT,
        # quantity TEXT,
        # quantity_photos TEXT,
        # check_in_date TEXT,
        # check_out_date TEXT,
        # price_min TEXT,
        # price_max TEXT,
        # distance INTEGER);""")
        # cur.execute("INSERT INTO best_deal_results(destinationID) VALUES (?)",
        # (destinationID,))
        # con.commit()
        if user.command == 'best deal_button_id':
            bot.send_message(user.user_id, text='Please type your minimum price($) for data to be shown')
            bot.register_next_step_handler(callback_obj.message, best_deal_max)
        elif user.command == 'low-price_button_id' or user.command == 'high price_button_id':
            bot.send_message(user.user_id, text='Excellent, now enter by digits how many hotels to show?'
                                                '\nThere should be no more than {}'.format(max_hotel_counter))
            bot.register_next_step_handler(callback_obj.message, answer_button)
        bot.answer_callback_query(callback_query_id=callback_obj.id)
        # bot.register_next_step_handler(callback_obj.message, best_deal_max)


def best_deal_max(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.min_price = message.text
    if user.min_price.isalpha():
        bot.send_message(user.user_id, text='Please try again, the price should be digits')
        bot.register_next_step_handler(message, best_deal_max)
    else:
        user.min_price = int(message.text)
        bot.send_message(user.user_id, "Good, now let's type your maximum price($)")
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(price_min) VALUES (?)", (min_price,))
        # con.commit()
        bot.register_next_step_handler(message, distance_confirmation)


def distance_confirmation(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.max_price = message.text
    if user.max_price.isalpha():
        bot.send_message(user.user_id, text='Please try again, the price should be digits')
        bot.register_next_step_handler(message, distance_confirmation)
    else:
        user.max_price = int(message.text)
        bot.send_message(user.user_id, "Good, now let's type your distance from the city center(km)",
                         )
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(price_max) VALUES (?)", (max_price,))
        # con.commit()
        bot.register_next_step_handler(message, distance_checking)


def distance_checking(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.distance = message.text
    if not user.distance.isalpha():
        user.distance = int(user.distance)
        bot.send_message(user.user_id, text='Excellent, now enter by digits how many hotels to show?'
                                            '\nThere should be no more than {}'.format(max_hotel_counter))
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(distance) VALUES (?)", (distance,))
        # con.commit()
        bot.register_next_step_handler(message, answer_button)
    else:
        bot.send_message(user.user_id, text="Try again, the distance should be digits")
        bot.register_next_step_handler(message, distance_checking)


def answer_button(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.hotels_count = int(message.text)
    if user.hotels_count <= max_hotel_counter:
        bot.send_message(user.user_id, 'Excellent, would you like see photos for itch one hotel?\n(Yes/no)',
                         reply_markup=gen_markup())
    elif max_hotel_counter < user.hotels_count < 1:
        bot.send_message(user.user_id, 'Error, please try again how many hotels to show?'
                                       '\nThere should be maximum {}'.format(max_hotel_counter))
        bot.register_next_step_handler(message, answer_button)
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(quantity) VALUES (?)", (hotel_number,))
        # con.commit()


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Как тебя зовут?")
    bot.set_state(message.chat.id, UserInfoState.city)


@bot.callback_query_handler(func=lambda call: call.data == 'cb_yes')
def callback_call_1(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.image_input = callback_obj.data
    # bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
    bot.send_message(user.user_id, "Number of photos for each hotel?(no more than {})"
                     .format(max_image_counter))
    # bot.send_photo((message.from_user.id, photo=photos[0], caption=text)
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, show_picture)


@bot.callback_query_handler(func=lambda call: call.data == 'cb_no')
def callback_call_2(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.image_input = callback_obj.data
    # bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
    bot.send_message(user.user_id, "No photos to be presented, now let's select your reservation dates"
                                   " for hotel booking", reply_markup='')
    start_booking_low(message=callback_obj.message.chat.id)
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    # bot.register_next_step_handler(callback_obj.message, picture_present)


def show_picture(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.quantity_count = int(message.text)
    if user.quantity_count <= max_image_counter:
        bot.send_message(user.user_id, 'Good, your request is accepted, now let is select your reservation dates'
                                       ' for hotel booking',
                         reply_markup='')
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(quantity_photos) VALUES (?)", (photos_num,))
        # con.commit()
        start_booking_low(message=user.user_id)
        #start_booking_low(message=message.chat.id)

# else:
# bot.reply_to(message, 'Type error please try again.')
# bot.register_next_step_handler(message, picture_present)

# @bot.message_handler(content_types='text', func=lambda message:
# bot.get_state(message.from_user.id) == range(1, max_hotel_counter + 1))
# def hotel_view(message: Message) -> None:
# states.quantity_count.value = message.text
# if bot.get_state(message.from_user.id):
# bot.edit_message_text(message.chat.id, message.message_id, text='Great, your data is confirmed')
# bot.set_state(message.from_user.id, states.image_input.value)
# bot.send_message(message.from_user.id, 'fg')
# bot.register_next_step_handler(message, get_name)
# @bot.message_handler(func=lambda message: message.text == range(1, max_image_counter + 1))
#   def low_price(message: Message) -> None:
#      name = message.text
#     UserInfoState.name = name
#    bot.send_message(message.from_user.id, f'{UserInfoState.name}, What city are you looking for an hotels?')

def start_booking_low(message) -> None:
    """
    Function which create and call calendar for selection of check in date
    :param message: according to menu /lowprice
    :return: None
    """
    user = Users.get_user(message)
    calendar, step = MyStyleCalendar(calendar_id=1, locale='en', min_date=datetime.datetime.today().date()).build()
    bot.send_message(user.user_id, f"Select {LSTEP[step]} at the first step", reply_markup=calendar)


def end_booking_low(message) -> None:
    """
    Function which create and call calendar for selection of check out date
    :param message: according to menu /lowprice
    :return: None
    """
    user = Users.get_user(message)
    calendar, step = MyStyleCalendar(calendar_id=2, locale='en', min_date=datetime.datetime.today().date()).build()
    bot.send_message(user.user_id, f"Select {LSTEP[step]} at the second step", reply_markup=calendar)


@bot.callback_query_handler(func=MyStyleCalendar.func(calendar_id=1))
def callback_calendar(call: CallbackQuery) -> None:
    """
    Handler for processing inline buttons of calendar where check in has made
    :param call: CallbackQuery
    :return: None
    """
    user = Users.get_user(call)
    result, key, step = MyStyleCalendar(calendar_id=1, locale='en',
                                        min_date=datetime.datetime.today().date()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Choose {LSTEP[step]} for check in", call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        user_id = call.from_user.id
        check_in_date = ''.join(str(result).split('-'))
        check_out_date = None
        with sq.connect(config_data.config.data_base) as con:
            cur = con.cursor()
            cur.execute(""" DROP TABLE IF EXISTS best_deal_results""")
            cur.execute(""" DROP TABLE IF EXISTS inter_results""")
            cur.execute(""" CREATE TABLE IF NOT EXISTS inter_results(
                                        user_id INTEGER PRIMARY KEY autoincrement,
                                        check_in_date TEXT,
                                        check_out_date TEXT);""")
            cur.execute(""" CREATE TABLE IF NOT EXISTS best_deal_results(
                            user_id INTEGER PRIMARY KEY autoincrement,
                            check_in_date TEXT,
                            check_out_date TEXT);""")
            cur.execute("INSERT INTO inter_results(user_id, check_in_date, check_out_date) VALUES (?, ?, ?)",
                        (user_id, check_in_date, check_out_date))
            cur.execute("INSERT INTO best_deal_results(user_id, check_in_date, check_out_date) VALUES (?, ?, ?)",
                        (user_id, check_in_date, check_out_date))
            con.commit()
            bot.edit_message_text(f"Your check in date is {result}", call.message.chat.id, call.message.message_id)
        logger.info(f"User {user_id} entered /bestdeal in function {start_message.__name__}")
        # end_booking_low(call.message, user_id)
        # data_set[call.message.chat.id]['check_in'] = result.strftime('%Y.%m.%d')
        # with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        # data['check in'] = result
        bot.send_message(chat_id=call.message.chat.id, text="Please choose from calendar check out date?")
        end_booking_low(message=call.message.chat.id)
        # bot.register_next_step_handler(call.message, check_out)


@bot.callback_query_handler(func=MyStyleCalendar.func(calendar_id=2))
def callback_calendar(call: CallbackQuery) -> None:
    """
    Handler for processing inline buttons of calendar where check out has made
    :param call: CallbackQuery
    :return: None
    """
    result, key, step = MyStyleCalendar(calendar_id=2, locale='en',
                                        min_date=datetime.datetime.today().date()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Choose {LSTEP[step]} for check out", call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        # user = Users.get_user(call.from_user.id)
        #user_id = call.from_user.id
        check_out_date = ''.join(str(result).split('-'))
        # write_check_date(id=user_id, check_out=check_out_date)
        with sq.connect(config_data.config.data_base) as con:
            cur = con.cursor()
            #cur.execute(""" DROP TABLE IF EXISTS inter_results""")
            cur.execute("INSERT INTO inter_results(check_out_date) VALUES (?)", (check_out_date,))
            cur.execute("INSERT INTO best_deal_results(check_out_date) VALUES (?)", (check_out_date,))
            con.commit()
        bot.edit_message_text(f"Your check out date is {result}", call.message.chat.id, call.message.message_id)
        # data_set[call.message.chat.id]['check_in'] = result.strftime('%Y.%m.%d')
        # with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        # data['check in'] = result
        # best_deal_min(message=call.message)
        bot.send_message(chat_id=call.message.chat.id, text="Excellent, the selection has done just two minutes...")
        # if call.data.startswith('best deal_'):
        user_info_bestdeal(message=call.message)
        # else:
        # user_info(message=call.message)
        bot.register_next_step_handler(call.message, start_message)


def user_info_bestdeal(message: Message):
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM best_deal_results")
        tuple_data = tuple(cur.fetchall())
        lst = [i for y in tuple_data for i in y]
        my_list = [i_elem for i_elem in lst if i_elem]
        print(my_list)
    user = Users.get_user(message.from_user.id)
    #user.get_user(user_id=user.user_id)
    try:
        with open('distance_calculation.json', 'w', encoding='utf-8') as file:
            json.dump(best_seller(user), file, indent=4,
                      ensure_ascii=False)
        with open('distance_calculation.json', 'r') as file:
            db = json.load(file)
            # db_str = file.read().strip()
            if not db:
                logger.info('{}, file not found'.format(None))
                bot.send_message(message.chat.id, 'According to your request no data found, '
                                                  'please change your searching parameters')
        for i_data in db:
            photo = photos(id_hotel=i_data.get('id_hotel'), user=user)
            card_info = f'Name: {i_data.get("name")}\n' \
                        f'Star rating: {i_data.get("star_rate")}\n' \
                        f'City: {i_data.get("city")}\n' \
                        f'Distance from the center: {i_data.get("distance from the center")}\n' \
                        f'Price per night: {i_data.get("price")} $\n' \
                        f'Total price: {(int(my_list[3]) - int(my_list[1])) * (round(i_data.get("price")))} $\n' \
                        f'Link: {i_data.get("link")}\n'
            for i_photo in photo:
                if i_photo and i_data:
                    bot.send_photo(message.chat.id, i_photo)
                    bot.send_message(message.chat.id, card_info)
            if len(my_list) < 15:
                # photo = photos(id_hotel=i_data.get('id_hotel'), quantity_photos=None)
                card_info = f'Name: {i_data.get("name", "")}\n' \
                            f'Star rating: {i_data.get("star_rate", "")}\n' \
                            f'City: {i_data.get("city", "")}\n' \
                            f'Distance from the center: {i_data.get("distance from the center", "")}\n' \
                            f'Price per night: {i_data.get("price", "")} $\n' \
                            f'Total price: {(int(my_list[13]) - int(my_list[11])) * (round(i_data.get("price", "")))} $\n' \
                            f'Link: {i_data.get("link", "none")}\n'
                bot.send_message(message.chat.id, card_info)
    except (TypeError, ValueError, FileNotFoundError) as exc:
        logger.exception(exc)
        bot.send_message(message.from_user.id, text=f'{exc}, according to your request no data present')


def user_info(message: Message):
    with sq.connect(config_data.config.data_base) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM inter_results")
        tpl = tuple(cur.fetchall())
        lst = [i for y in tpl for i in y]
        my_lst = [i_elem for i_elem in lst if i_elem]
        print(my_lst)
    try:
        with open('hotel_suggestions.json', 'w', encoding="utf-8") as file:
            json.dump(hotel_suggestions_highest(city_id=str(lst[1]), quantity=lst[8]), file, indent=4,
                      ensure_ascii=False)
        with open('hotel_suggestions.json') as file:
            data = json.load(file)
        for i_hotel in data:
            photo = photos(id_hotel=i_hotel.get('id_hotel'), quantity_photos=lst[15])
            if len(lst) == 30:
                card = f'Name: {i_hotel.get("name")}\n' \
                       f'Star rating: {i_hotel.get("star_rate")}\n' \
                       f'Address: {i_hotel.get("Address")}\n' \
                       f'City: {i_hotel.get("city")}\n' \
                       f'Distance from the center: {i_hotel.get("distance from the center")}\n' \
                       f'Price per night: {i_hotel.get("price")} $\n' \
                       f'Total price: {((len(lst) - 1) - (len(lst) - 8)) * round(i_hotel.get("price"), 2)} $\n' \
                       f'Link: {i_hotel.get("link")}\n'
                for i_photo in photo:
                    bot.send_photo(message.chat.id, i_photo)
                    bot.send_message(message.chat.id, card)
            else:
                card = f'Name: {i_hotel.get("name")}\n' \
                       f'Star rating: {i_hotel.get("star_rate")}\n' \
                       f'Address: {i_hotel.get("Address")}\n' \
                       f'City: {i_hotel.get("city")}\n' \
                       f'Distance from the center: {i_hotel.get("distance from the center")}\n' \
                       f'Price per night: {i_hotel.get("price")} $\n' \
                       f'Total price: {((len(lst) - 1) - (len(lst) - 8)) * round(i_hotel.get("price"), 2)} $\n' \
                       f'Link: {i_hotel.get("link")}\n'
                bot.send_message(message.chat.id, card)

        # for i_elem, j_elem in i_hotel.items():
    except UnicodeEncodeError as exc:
        logger.exception(exc)


def check_out(message: Message) -> None:
    if not message.text.isdigit():
        bot.send_message(chat_id=message.chat.id,
                         text='Error, please enter the digits how long would you like to stay?')
    elif 1 > int(message.text) > 30:
        bot.send_message(chat_id=message.chat.id, text='Please try again')
    else:
        data_set[message.chat.id][
            'check_out'] = f"{(datetime.datetime.strptime(data_set[message.chat.id]['check_in'], '%d.%m.%Y'))}"


# + datetime.timedelta(days=int(message.text))).strftime('%d.%m.%Y')}"
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
