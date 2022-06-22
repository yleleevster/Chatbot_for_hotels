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
from states.contact_info import max_hotel_counter, max_image_counter, Users, user

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
    if user.command.lower() == '/start' or user.command.lower() == '/hello-world' or user.command.lower() == '/привет':
        bot.send_message(user.user_id, f'Hello {user.user_id}.\n'
                                       f'Could be glad help you.\n'
                                       f'Below you can find a commands which could direct you about hotels'
                                       f'to be chosen. For other quations please push the button /help.')

        key_board = types.InlineKeyboardMarkup(row_width=1)
        lowprice = types.InlineKeyboardButton(text='/lowprice', callback_data='low-price_button_id')
        highprice = types.InlineKeyboardButton(text='/highprice', callback_data='high price_button_id')
        bestdeal = types.InlineKeyboardButton(text='/bestdeal', callback_data='best deal_button_id')
        history = types.InlineKeyboardButton(text='/history', callback_data='history_button_id')
        key_board.add(lowprice, highprice, bestdeal, history)
        bot.send_message(message.chat.id, 'Choose from menu', reply_markup=key_board)
    else:
        text = '/start, /Hi, /hello-world/ - to begin work with chatbot.\n' \
               '/lowprice  - To find cheapest hotels in the city.\n' \
               '/highprice - To find most expensive hotels in the city.\n' \
               '/bestdeal  - To see the most suitable for the price and location from the center.\n' \
               '/hystory   - To view histories about hotels.'

        bot.send_message(user.user_id, text=text)


@bot.callback_query_handler(func=lambda callback: callback.data == 'low-price_button_id')
def check_callback_data_1(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    data_set['command_low'] = user.command
    data_set['date time low'] = user.datetime
    logger.info(f"User {user.user_id} entered {user.command} at {user.datetime} in function {start_message.__name__}")
    bot.send_message(user.user_id, 'In which city are you looking for a hotel?')
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, request_city)


@bot.callback_query_handler(func=lambda callback: callback.data == 'high price_button_id')
def check_callback_data_2(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    data_set['command_high'] = user.command
    data_set['date time high'] = user.datetime
    logger.info(f"User {user.user_id} entered {user.command} at {user.datetime} in function {start_message.__name__}")
    bot.send_message(user.user_id, 'In which city are you looking for a hotel?')
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, request_city)


@bot.callback_query_handler(func=lambda callback: callback.data == 'best deal_button_id')
def check_callback_data_3(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    # callback_obj.data = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    data_set['command_best_deal'] = user.command
    data_set['date time bestdeal'] = user.datetime
    logger.info(f"User {user.user_id} entered {user.command} at {user.datetime} in function {start_message.__name__}")
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
    data_set['city_id'] = user.destinationId
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
    data_set['min_price'] = user.min_price
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
    data_set['max_price'] = user.max_price
    if user.max_price.isalpha():
        bot.send_message(user.user_id, text='Please try again, the price should be digits')
        bot.register_next_step_handler(message, distance_confirmation)
    else:
        user.max_price = int(message.text)
        bot.send_message(user.user_id, "Good, now let's type your distance from the city center(km)")
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(price_max) VALUES (?)", (max_price,))
        # con.commit()
        bot.register_next_step_handler(message, distance_checking)


def distance_checking(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.distance = message.text
    data_set['distance'] = user.distance
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
    if user.hotels_count in range(1, max_hotel_counter + 1):
        data_set['hotel_quantity'] = str(user.hotels_count)
        bot.send_message(user.user_id, 'Excellent, would you like see photos for itch one hotel?\n(Yes/no)',
                         reply_markup=gen_markup())
    elif int(user.hotels_count) < 1 or int(user.hotels_count) > max_hotel_counter:
        bot.send_message(user.user_id, 'Error, please try again how many hotels to show?'
                                       '\nThere should be maximum {} no more'.format(max_hotel_counter))
        bot.register_next_step_handler(message, answer_button)
        return
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(quantity) VALUES (?)", (hotel_number,))
        # con.commit()


@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой. Как тебя зовут?")
    # bot.set_state(message.chat.id, UserInfoState.city)


@bot.callback_query_handler(func=lambda call: call.data == 'cb_yes')
def callback_call_1(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.image_input = callback_obj.data
    data_set['yes'] = user.image_input
    # bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
    bot.send_message(user.user_id, "Number of photos for each hotel?(no more than {})"
                     .format(max_image_counter))
    # bot.send_photo((message.from_user.id, photo=photos[0], caption=text)
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, show_picture)


@bot.callback_query_handler(func=lambda call: call.data == 'cb_no')
def callback_call_2(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.image_exit = callback_obj.data
    data_set['no'] = user.image_exit
    # bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
    bot.send_message(user.user_id, "No photos to be presented, now let's select your reservation dates"
                                   " for hotel booking", reply_markup='')
    start_booking_low(message=callback_obj.message.chat.id)
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    # bot.register_next_step_handler(callback_obj.message, picture_present)


def show_picture(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.quantity_count = int(message.text)
    if user.quantity_count in range(1, max_image_counter + 1):
        data_set['photo_quantity'] = user.quantity_count
        bot.send_message(user.user_id, "Good, your request is accepted, now let's select your reservation dates"
                                       " for hotel booking",
                         reply_markup='')
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute("INSERT INTO best_deal_results(quantity_photos) VALUES (?)", (photos_num,))
        # con.commit()
        start_booking_low(message=user.user_id)
        # start_booking_low(message=message.chat.id)
    elif user.quantity_count == 0 or user.quantity_count > max_image_counter:
        bot.send_message(user.user_id, "Please try again, amount of pictures should be no more than {}".
                         format(max_image_counter))
        bot.register_next_step_handler(message, show_picture)
        return


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
        user.check_in = check_in_date
        data_set['check in'] = int(user.check_in)
        # check_out_date = None
        # with sq.connect(config_data.config.data_base) as con:
        # cur = con.cursor()
        # cur.execute(""" DROP TABLE IF EXISTS best_deal_results""")
        # cur.execute(""" DROP TABLE IF EXISTS inter_results""")
        # cur.execute(""" CREATE TABLE IF NOT EXISTS inter_results(
        #                            user_id INTEGER PRIMARY KEY autoincrement,
        #                            check_in_date TEXT,
        #                            check_out_date TEXT);""")
        # cur.execute(""" CREATE TABLE IF NOT EXISTS best_deal_results(
        #                user_id INTEGER PRIMARY KEY autoincrement,
        #                check_in_date TEXT,
        #                check_out_date TEXT);""")
        # cur.execute("INSERT INTO inter_results(user_id, check_in_date, check_out_date) VALUES (?, ?, ?)",
        #            (user_id, check_in_date, check_out_date))
        # cur.execute("INSERT INTO best_deal_results(user_id, check_in_date, check_out_date) VALUES (?, ?, ?)",
        #            (user_id, check_in_date, check_out_date))
        # con.commit()
        bot.edit_message_text(f"Your check in date is {result}", call.message.chat.id, call.message.message_id)
        logger.info(f"User {user_id} entered {check_in_date} in function {callback_calendar.__name__}")
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
        user = Users.get_user(call.from_user.id)
        # user_id = call.from_user.id
        check_out_date = ''.join(str(result).split('-'))
        user.check_out = check_out_date
        data_set['check out'] = int(user.check_out)
        # with sq.connect(config_data.config.data_base) as con:
        #    cur = con.cursor()
        #    # cur.execute(""" DROP TABLE IF EXISTS inter_results""")
        #    cur.execute("INSERT INTO inter_results(check_out_date) VALUES (?)", (check_out_date,))
        #    cur.execute("INSERT INTO best_deal_results(check_out_date) VALUES (?)", (check_out_date,))
        #    con.commit()
        bot.edit_message_text(f"Your check out date is {result}", call.message.chat.id, call.message.message_id)
        logger.info(f"User {user.user_id} entered {check_out_date} in function {callback_calendar.__name__}")
        # data_set[call.message.chat.id]['check_in'] = result.strftime('%Y.%m.%d')
        # with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        # data['check in'] = result
        # best_deal_min(message=call.message)
        bot.send_message(chat_id=call.message.chat.id, text="Excellent, the selection has done just two minutes...")
        # if call.data.startswith('best deal_'):
        if user.command == 'low-price_button_id' or user.command == 'high price_button_id':
            user_info(message=call.message)
        elif user.command == 'best deal_button_id':
            user_info_bestdeal(message=call.message)
        bot.register_next_step_handler(call.message, start_message)


def user_info_bestdeal(message: Message):
    user = Users.get_user(message.from_user.id)
    # with sq.connect(config_data.config.data_base) as con:
    #    cur = con.cursor()
    #    cur.execute("SELECT * FROM best_deal_results")
    #    tuple_data = tuple(cur.fetchall())
    #    lst = [i for y in tuple_data for i in y]
    #    my_list = [i_elem for i_elem in lst if i_elem]
    #    print(my_list)
    # user = Users.get_user(message.from_user.id)
    print(data_set)
    try:
        with open('distance_calculation.json', 'w', encoding='utf-8') as file:
            json.dump(best_seller(city_id=data_set.get('city_id'), quantity=data_set.get('hotel_quantity'),
                                  min_price=data_set.get('min_price'), max_price=data_set.get('max_price'),
                                  distance=data_set.get('distance')), file, indent=4, ensure_ascii=False)
        with open('distance_calculation.json', 'r') as file:
            db = json.load(file)
            # db_str = file.read().strip()
            if not db:
                logger.info('{}, file not found'.format(None))
                bot.send_message(message.chat.id, 'According to your request no data found, '
                                                  'please change your searching parameters')
        for i_data in db:
            if user.image_input == 'cb_yes':
                photo = photos(id_hotel=i_data.get('id_hotel'), quantity_photos=data_set.get('photo_quantity'))
                info = f'Name: {i_data.get("name")}\n' \
                       f'Star rating: {i_data.get("star_rate")}\n' \
                       f'City: {i_data.get("city")}\n' \
                       f'Distance from the center: {i_data.get("distance from the center")}\n' \
                       f'Price per night: {i_data.get("price")} $\n' \
                       f'Total price: {(data_set.get("check out") - data_set.get("check in")) * (round(i_data.get("price")))} $\n' \
                       f'Link: {i_data.get("link")}\n'
                for i_photo in photo:
                    if i_photo and i_data:
                        bot.send_photo(message.chat.id, i_photo)
                        bot.send_message(message.chat.id, info)
            elif user.image_exit == 'cb_no':    #data_set.get('no') == 'cb_no'
                # photo = photos(id_hotel=i_data.get('id_hotel'), quantity_photos=None)
                card_info = f'Name: {i_data.get("name", "")}\n' \
                            f'Star rating: {i_data.get("star_rate", "")}\n' \
                            f'City: {i_data.get("city", "")}\n' \
                            f'Distance from the center: {i_data.get("distance from the center", "")}\n' \
                            f'Price per night: {i_data.get("price", "")} $\n' \
                            f'Total price: {(data_set.get("check out") - data_set.get("check in")) * (round(i_data.get("price", "")))} $\n' \
                            f'Link: {i_data.get("link", "none")}\n'
                bot.send_message(message.chat.id, card_info)
                data_set.clear()
    except (TypeError, ValueError, FileNotFoundError) as exc:
        logger.exception(exc)
        bot.send_message(message.from_user.id, text=f'{exc}, according to your request no data present')


def user_info(message: Message):
    # with sq.connect(config_data.config.data_base) as con:
    #    cur = con.cursor()
    #    cur.execute("SELECT * FROM inter_results")
    #    tpl = tuple(cur.fetchall())
    #    lst = [i for y in tpl for i in y]
    #    my_lst = [i_elem for i_elem in lst if i_elem]
    #    print(my_lst)
    print(data_set)
    try:
        with open('hotel_suggestions.json', 'w', encoding="utf-8") as file:
            json.dump(hotel_suggestions_highest(city_id=data_set.get('city_id'),
                                                quantity=data_set.get('hotel_quantity')), file, indent=4,
                      ensure_ascii=False)
        with open('hotel_suggestions.json') as file:
            data = json.load(file)
            if not data:
                logger.info('{}, file not found'.format(None))
                bot.send_message(message.chat.id, 'According to your request no data found, '
                                                  'please change your searching parameters')
        for i_hotel in data:
            if user.image_input == 'cb_yes':
                photo = photos(id_hotel=i_hotel.get('id_hotel'), quantity_photos=data_set.get('photo_quantity'))
                card = f'Name: {i_hotel.get("name")}\n' \
                       f'Star rating: {i_hotel.get("star_rate")}\n' \
                       f'Address: {i_hotel.get("Address")}\n' \
                       f'City: {i_hotel.get("city")}\n' \
                       f'Distance from the center: {i_hotel.get("distance from the center")}\n' \
                       f'Price per night: {i_hotel.get("price")} $\n' \
                       f'Total price: {(data_set.get("check out") - data_set.get("check in")) * (round(i_hotel.get("price")))} $\n' \
                       f'Link: {i_hotel.get("link")}\n'
                for i_photo in photo:
                    bot.send_photo(message.chat.id, i_photo)
                    bot.send_message(message.chat.id, card)
            elif user.image_exit == 'cb_no':
                card = f'Name: {i_hotel.get("name")}\n' \
                       f'Star rating: {i_hotel.get("star_rate")}\n' \
                       f'Address: {i_hotel.get("Address")}\n' \
                       f'City: {i_hotel.get("city")}\n' \
                       f'Distance from the center: {i_hotel.get("distance from the center")}\n' \
                       f'Price per night: {i_hotel.get("price")} $\n' \
                       f'Total price: {(data_set.get("check out") - data_set.get("check in")) * (round(i_hotel.get("price")))} $\n' \
                       f'Link: {i_hotel.get("link")}\n'
                bot.send_message(message.chat.id, card)
        # for i_elem, j_elem in i_hotel.items():
    except (UnicodeEncodeError, TypeError, ValueError, FileNotFoundError) as exc:
        logger.exception(exc)


bot.polling(none_stop=True, interval=2)
