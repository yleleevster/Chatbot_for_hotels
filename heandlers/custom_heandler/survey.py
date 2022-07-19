from loguru import logger
from telebot.types import CallbackQuery
from telegram_bot_calendar import WYearTelegramCalendar, LSTEP
from config_data.config import bot
from database.history_real import *
from keyboard.reply.contacts import gen_markup, hotel_suggestions, media_group_creation, \
    photos, request_city_markup, best_seller, command_gen
from states.contact_info import max_hotel_counter, max_image_counter, Users

data_set = dict()


class MyStyleCalendar(WYearTelegramCalendar):
    """ Class for custom style of representation """
    prev_button = "⬅️"
    next_button = "➡️"
    empty_month_button = ""
    empty_year_button = ""


with db:
    db.create_tables([HistoryOutput])


@bot.message_handler(content_types=['text'])
def start_message(message: Message) -> None:
    user = Users.get_user(message.chat.id)
    user.command = message.text
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    data_set.clear()
    data_set['command'] = user.command
    data_set['date of command'] = user.datetime
    if user.command.lower() in ('/start', '/hello-world', '/Hi'):
        final_mess = f'Hello {message.chat.first_name}!\nI am chatbot from travel agency "Too Easy Travel".\n' \
                     f'Below you can find a commands which could direct you about hotels to be chosen. ' \
                     f'For more information please push the button /help.'
        logger.info(f'User {user.user_id} entered {user.command} at {user.datetime}')
        bot.send_message(user.user_id, text=final_mess)
        bot.send_message(message.chat.id, 'Choose from menu', reply_markup=command_gen())
    elif user.command.lower() == '/lowprice' or user.command.lower() == '/highprice' or \
            user.command.lower() == '/bestdeal':
        user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        logger.info(
            f"User {user.user_id} entered {user.command} at {user.datetime} in function {start_message.__name__}")
        bot.send_message(user.user_id, 'In which city are you looking for a hotel?')
        bot.register_next_step_handler(message, request_city)
    elif user.command.lower() == '/history':
        hist_data = hist_get_out(user_id=user.user_id)
        try:
            if hist_data:
                for i_hist in hist_data:
                    bot.send_message(user.user_id, text=i_hist)
                    bot.register_next_step_handler(message, start_message)
            else:
                bot.send_message(user.user_id, 'The history is empty,\nso choose next commands: ',
                                 reply_markup=command_gen())
        except Exception as exc:
            logger.exception(exc)
        logger.info(
            f'User {user.user_id} entered {user.command} at {user.datetime} in function {start_message.__name__}')
    else:
        text = '/start, /hello-world, /Hi - to begin work with chatbot.\n' \
               '/lowprice  - To find cheapest hotels in the city.\n' \
               '/highprice - To find most expensive hotels in the city.\n' \
               '/bestdeal  - To see the most suitable for the price and location from the center.\n' \
               '/history   - To view histories about hotels.'
        bot.send_message(user.user_id, text=text)


@bot.callback_query_handler(func=lambda callback: callback.data in ['/lowprice', '/highprice', '/bestdeal'])
@logger.catch()
def check_callback_data_1(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    data_set['command'] = user.command
    data_set['date of command'] = user.datetime
    logger.info(f"User {user.user_id} entered {user.command} at {user.datetime} in function {start_message.__name__}")
    bot.send_message(user.user_id, 'In which city are you looking for a hotel?')
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, request_city)


@bot.callback_query_handler(func=lambda callback: callback.data == '/history')
@logger.catch()
def check_callback_data_2(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.datetime = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    user.command = callback_obj.data
    if user.command == '/history':
        hist_data = hist_get_out(user_id=user.user_id)
        try:
            if hist_data:
                for i_data in hist_data:
                    bot.send_message(user.user_id, text=i_data)
                    bot.register_next_step_handler(callback_obj.message, start_message)
            else:
                bot.send_message(user.user_id, text='The history is empty, choose next commands: ',
                                 reply_markup=command_gen())
        except Exception as exc:
            logger.exception(exc)
    logger.info(f"User {user.user_id} entered {user.command} at {user.datetime} in function {start_message.__name__}")
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, start_message)


@logger.catch()
def request_city(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.city = message.text
    collect_data = request_city_markup(name=user.city)
    if collect_data:
        if user.city.isdigit():
            bot.send_message(user.user_id, text='Type error, city should be letters, try again')
            bot.register_next_step_handler(message, request_city)
        elif user.city in ['/highprice', '/lowprice', '/bestdeal', '/history', '/start', '/help']:
            bot.send_message(user.user_id, text='No place to commands, enter city name')
            bot.register_next_step_handler(message, request_city)
        else:
            logger.info(f'User {user.user_id} entered city {user.city} in function {request_city.__name__}')
            bot.send_message(user.user_id, 'Fine, you have chosen {}, please specify:'.format(user.city),
                             reply_markup=collect_data)  # Отправляем кнопки с вариантами
    else:
        bot.send_message(user.user_id, text='A city does not exists, please write again')
        bot.register_next_step_handler(message, request_city)


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def callback_validation(callback_obj: CallbackQuery) -> None:
    user = Users.get_user(callback_obj.from_user.id)
    destination_id = callback_obj.data[5:]
    user.destinationId = destination_id
    if not callback_obj.data.isalpha():
        data_set['city_id'] = str(user.destinationId)
        bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
                              text=f'Good, your request is confirmed.')
        if user.command == '/bestdeal':
            bot.send_message(user.user_id, text='Please type your minimum price for data to be shown ($)')
            bot.register_next_step_handler(callback_obj.message, best_deal_max)
        elif user.command == '/lowprice' or user.command == '/highprice':
            bot.send_message(user.user_id, text='Excellent, now enter by digits how many hotels to show?'
                                                '\nThere should be no more than {}'.format(max_hotel_counter))
            bot.register_next_step_handler(callback_obj.message, answer_button)
        bot.answer_callback_query(callback_query_id=callback_obj.id)


@logger.catch()
def best_deal_max(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.min_price = message.text
    if user.min_price.isalpha():
        bot.send_message(user.user_id, text='Please try again, the price should be digits')
        logger.debug(f'Error, user has entered text message')
        bot.register_next_step_handler(message, best_deal_max)
    elif user.min_price.isdigit():
        data_set['min price'] = str(user.min_price)
        bot.send_message(user.user_id, "Good, now let's type your maximum price($)")
        logger.info(f'User has entered {user.min_price} in function {callback_validation.__name__}')
        bot.register_next_step_handler(message, distance_confirmation)


@logger.catch()
def distance_confirmation(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.max_price = message.text
    if user.max_price.isalpha():
        bot.send_message(user.user_id, text='Please try again, the price should be digits')
        logger.debug(f'Error, user has entered {user.min_price} as text message in function {best_deal_max.__name__}')
        bot.register_next_step_handler(message, distance_confirmation)
    elif user.max_price.isdigit():
        data_set['max price'] = str(user.max_price)
        bot.send_message(user.user_id, "Good, now let's type your distance from the city center(km)")
        logger.info(f'User has entered {user.max_price} in function {best_deal_max.__name__}')
        bot.register_next_step_handler(message, distance_checking)


@logger.catch()
def distance_checking(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.distance = message.text
    if not user.distance.isalpha():
        user.distance = int(user.distance)
        data_set['distance'] = user.distance
        bot.send_message(user.user_id, text='Excellent, now enter by digits how many hotels to show?'
                                            '\nThere should be no more than {}'.format(max_hotel_counter))
        bot.register_next_step_handler(message, answer_button)
    else:
        bot.send_message(user.user_id, text="Try again, the distance should be digits")
        logger.error(f'Error, user has entered {user.distance} as text message')
        bot.register_next_step_handler(message, distance_checking)


@logger.catch()
def answer_button(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.hotels_count = message.text
    if not user.hotels_count.isalpha():
        user.hotels_count = int(user.hotels_count)
        if user.hotels_count in range(1, max_hotel_counter + 1):
            data_set['hotel quantity'] = str(user.hotels_count)
            logger.info(f'User has typed a {user.hotels_count} hotels in function {callback_validation.__name__}')
            bot.send_message(user.user_id, 'Excellent, would you like see photos for itch one hotel?\n(Yes/no)',
                             reply_markup=gen_markup())
        elif user.hotels_count < 1 or user.hotels_count > max_hotel_counter:
            bot.send_message(user.user_id, 'Error, please try again how many hotels to show?'
                                           '\nThere should be maximum {}'.format(max_hotel_counter))
            logger.error(f'Error, user has entered required number - {user.hotels_count} out of range')
            bot.register_next_step_handler(message, answer_button)
    else:
        bot.send_message(user.user_id, 'Error, an amount of hotels should be digits, try again')
        logger.error(f'Error, user has entered {user.hotels_count} as text message')
        bot.register_next_step_handler(message, answer_button)


@bot.message_handler(content_types=['text'])
def cmd_reset(message: Message):
    user = Users.get_user(message.chat.id)
    user.command = message.text
    bot.send_message(user.user_id, "Choose again from commands:",  reply_markup=command_gen())
    # start_message(message)


@bot.callback_query_handler(func=lambda call: call.data == 'cb_yes')
def callback_call_1(callback_obj):
    user = Users.get_user(callback_obj.from_user.id)
    user.image_input = callback_obj.data
    data_set['yes'] = user.image_input
    bot.send_message(user.user_id, "Number of photos for each hotel?(no more than {})"
                     .format(max_image_counter))
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


def show_picture(message: Message) -> None:
    user = Users.get_user(message.from_user.id)
    user.quantity_count = int(message.text)
    if user.quantity_count in range(1, max_image_counter + 1):
        data_set['picture number'] = user.quantity_count
        bot.send_message(user.user_id, 'Good, your request is accepted, now let is select your reservation dates'
                                       ' for hotel booking',
                         reply_markup='')
        start_booking_low(message=user.user_id)


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
        bot.edit_message_text(f"Your check in date is {result}", call.message.chat.id, call.message.message_id)
        logger.info(f"User {user_id} selected check-in date {user.check_in} in function {callback_calendar.__name__}")
        bot.send_message(chat_id=call.message.chat.id, text="Please choose from calendar check out date?")
        end_booking_low(message=call.message.chat.id)


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
        check_out_date = ''.join(str(result).split('-'))
        user.check_out = check_out_date
        data_set['check out'] = int(user.check_out)
        bot.edit_message_text(f"Your check out date is {result}", call.message.chat.id, call.message.message_id)
        logger.info(
            f"User {user.user_id} selected check-out date {user.check_out} in function {callback_calendar.__name__}")
        bot.send_message(chat_id=call.message.chat.id, text="Excellent, the selection has done just two minutes...")
        if user.command == '/bestdeal':
            user_info_bestdeal(message=call.message)
        elif user.command == '/lowprice':
            user_info_low_high(message=call.message, com_filter='PRICE')
        else:
            user_info_low_high(message=call.message, com_filter='PRICE_HIGHEST_FIRST')
        bot.register_next_step_handler(call.message, start_message)


def user_info_bestdeal(message: Message) -> None:
    """
    Function that output hotel's information included pictures according to specific parameters of the user requests,
    such as best deal sorting.
    :param message:
    :return:
    """
    user = Users.get_user(message.chat.id)
    try:
        bs = best_seller(city_id=data_set.get('city_id'), quantity=data_set.get('hotel quantity'),
                         min_price=data_set.get('min price'), max_price=data_set.get('max price'),
                         distance=data_set.get('distance'))
        if not bs:
            logger.info('{}, file not found'.format(None))
            bot.send_message(message.chat.id, 'According to your request no data found, '
                                              'please change your searching parameters /help')

        else:
            list_of_hotels = []
            for db_info in bs:
                card_info = f'Name: {db_info.get("name")}\n' \
                            f'Star rating: {round(float(db_info.get("star_rate")))}\n' \
                            f'Address: {db_info.get("Address")}\n' \
                            f'City: {db_info.get("city")}\n' \
                            f'Distance from the center: {db_info.get("distance from the center")}\n' \
                            f'Price per night: {round(float(db_info.get("price")))} $\n' \
                            f'Total price: ' \
                    f'{(data_set.get("check out") - data_set.get("check in")) * (round(float(db_info.get("price"))))}' \
                            f' $\n' \
                            f'Link: {db_info.get("link")}\n'
                list_of_hotels.append(db_info.get('name'))
                if user.image_input == 'cb_yes':
                    photo = photos(id_hotel=db_info.get('id_hotel'), quantity_photos=data_set.get('picture number'))
                    inter_media = media_group_creation(pics=photo)
                    if db_info and len(inter_media) != 0:
                        try:
                            bot.send_media_group(message.chat.id, inter_media)
                            bot.send_message(message.chat.id, card_info, disable_web_page_preview=True)
                        except (Exception, FileNotFoundError) as exc:
                            logger.exception(exc)
                    else:
                        bot.send_message(message.from_user.id, text='According to your request no photo found')
                elif user.image_exit == 'cb_no':
                    bot.send_message(message.chat.id, card_info, disable_web_page_preview=True)
            history_writing(message=message, hotel_list='\n'.join(list_of_hotels), command=user.command)
            bot.send_message(message.chat.id, 'Your request was successfully completed')
    except (TypeError, ValueError, FileNotFoundError) as exc:
        logger.exception(exc)
        bot.send_message(message.from_user.id, text=f'{exc}, according to your request no data present')


def user_info_low_high(message: Message, com_filter: str) -> None:
    """
    Function that output hotel's information included pictures according to specific parameters of the user requests,
    such as low or high price sorting.
    :param message:
    :param com_filter:
    :return:
    """
    user = Users.get_user(message.chat.id)
    try:
        res = hotel_suggestions(city_id=data_set.get('city_id'), quantity=data_set.get('hotel quantity'),
                                sortorder=com_filter)
        if not res:
            logger.info('{}, file not found'.format(None))
            bot.send_message(message.chat.id, 'According to your request no data found, '
                                              'please change your searching parameters /help')
        else:
            hotel_list = list()
            for i_hotel in res:
                card = f'Name: {i_hotel.get("name")}\n' \
                       f'Star rating: {round(float(i_hotel.get("star_rate")))}\n' \
                       f'Address: {i_hotel.get("Address")}\n' \
                       f'City: {i_hotel.get("city")}\n' \
                       f'Distance from the center: {i_hotel.get("distance from the center")}\n' \
                       f'Price per night: {round(float(i_hotel.get("price")))} $\n' \
                       f'Total price: ' \
                    f'{(data_set.get("check out") - data_set.get("check in")) * (round(float(i_hotel.get("price"))))}' \
                       f' $\n' \
                       f'Link: {i_hotel.get("link")}\n'
                hotel_list.append(i_hotel.get('name'))
                if user.image_input == 'cb_yes':
                    photo = photos(id_hotel=i_hotel.get('id_hotel'), quantity_photos=data_set.get('picture number'))
                    inter_media = media_group_creation(pics=photo)
                    if i_hotel and len(inter_media) != 0:
                        try:
                            bot.send_media_group(message.chat.id, inter_media)
                            bot.send_message(message.chat.id, card, disable_web_page_preview=True)
                        except (Exception, FileNotFoundError) as exc:
                            logger.exception(exc)
                    else:
                        bot.send_message(message.from_user.id, text='According to your request no photo found')
                elif user.image_exit == 'cb_no':
                    bot.send_message(message.chat.id, card, disable_web_page_preview=True)
            history_writing(message=message, hotel_list='\n'.join(hotel_list), command=user.command)
            bot.send_message(message.chat.id, 'Your request was successfully completed')
    except (UnicodeEncodeError, TypeError, ValueError, FileNotFoundError) as exc:
        logger.exception(exc)


bot.polling(none_stop=True, interval=2)
