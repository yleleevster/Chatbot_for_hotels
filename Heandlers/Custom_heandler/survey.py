import datetime
from telebot import types
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import WYearTelegramCalendar, LSTEP
from Config_data.config import bot
from Keyboard.reply.contacts import city_markup, gen_markup, get_pictures, request_contact
from States.Contact_info import max_hotel_counter, max_image_counter, UserInfoState


data_set = dict()
class MyStyleCalendar(WYearTelegramCalendar):
    """ Class for custom style of representation """
    prev_button = "⬅️"
    next_button = "➡️"
    empty_month_button = ""
    empty_year_button = ""


@bot.message_handler(content_types=['text'])
def start_message(message: Message) -> None:
    if message.text.lower() == '/start' or message.text.lower() == '/hello-world' or message.text.lower() == 'привет':
        bot.send_message(message.from_user.id, f'Hello {message.from_user.id}.\n'
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
        bot.send_message(message.from_user.id, f'/start - to begin work with chatbot.\n'
                                               f'/lowprice - To find cheapest hotels in the city.\n'
                                               f'/highprice - To find most expensive hotels in the city.\n'
                                               f'/bestdeal - To see the most suitable for the price and location from'
                                               f' the center.\n'
                                               f'/hystory - To view histories about hotels.')


@bot.callback_query_handler(func=lambda callback: callback.data == 'low-price_button_id')
def check_callback_data(callback):
    if callback.data:
        bot.send_message(callback.message.chat.id, 'In which city are you looking for a hotel?')
        bot.register_next_step_handler(callback.message, city_1)
    # elif callback.data == 'high price_button_id':
    # bot.register_next_step_handler(callback.message, city_1)


def city_1(message: Message) -> None:
    res = city_markup(message.text)
    if res:
        bot.send_message(message.from_user.id, 'Please, clarify:',
                         reply_markup=res)  # Отправляем кнопки с вариантами
    # else:
    # bot.send_message(message.chat.id, 'Please try again')
    # bot.register_next_step_handler(message, check_callback_data)


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def callback_cheking(callback_obj: CallbackQuery) -> None:
    # call_data = '_'.join(call.data.split('_')[1:])
    callback_obj.data = callback_obj.data[6:]
    # if call.message:
    if not callback_obj.data.isalpha():
        bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
                              text='Good, your request is confirmed')
        bot.send_message(callback_obj.from_user.id, 'now enter by digits how many hotels to show?'
                                                    '\nThere should be no more than {}'.format(max_hotel_counter))
    elif max_hotel_counter < int(callback_obj.data) < 1:
        bot.send_message(callback_obj.from_user.id, 'Error, please try again how many hotels to show?'
                                                    '\nThere should be maximum'
                                                    ' {}'.format(max_hotel_counter))
        bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, hotel_button)

    # bot.edit_message_text(call.message.chat.id, call.message.message_id, reply_markup=None)
    # logging.info(f'call={call.data}')


@bot.message_handler(func=lambda message: message.text == range(1, max_hotel_counter + 1))
def hotel_button(message: Message) -> None:
    if message.text:
        bot.send_message(message.chat.id, 'Excellent, would you like see photos for itch one of hotel?\n(Yes/no)',
                         reply_markup=gen_markup())
        bot.register_next_step_handler(message, callback_1)
    # else:
    # bot.reply_to(message, 'Type error please try again.')
    # bot.register_next_step_handler(message, hotel_button)


# @bot.message_handler(content_types='text', func=lambda message:
# bot.get_state(message.from_user.id) == range(1, max_hotel_counter + 1))
# def hotel_view(message: Message) -> None:
# States.quantity_count.value = message.text
# if bot.get_state(message.from_user.id):
# bot.edit_message_text(message.chat.id, message.message_id, text='Great, your data is confirmed')
# bot.set_state(message.from_user.id, States.image_input.value)
# bot.send_message(message.from_user.id, 'fg')
# bot.register_next_step_handler(message, get_name)
@bot.callback_query_handler(func=lambda call: call.data == 'cb_yes')
def callback_1(callback_obj):
    #bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
                          #text='Number of photos for each hotel?(no more than {})'.format(max_image_counter))
    bot.send_message(callback_obj.from_user.id, "Number of photos for each hotel?(no more than {})"
                     .format(max_image_counter))
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, picture_present)


@bot.callback_query_handler(func=lambda call: call.data == 'cb_no')
def callback_2(callback_obj):
    #bot.edit_message_text(chat_id=callback_obj.message.chat.id, message_id=callback_obj.message.message_id,
                          #text='No photos to be presented')
    bot.send_message(callback_obj.from_user.id, "No photos to be presented")
    bot.answer_callback_query(callback_query_id=callback_obj.id)
    bot.register_next_step_handler(callback_obj.message, picture_present)


@bot.message_handler(func=lambda message: message.text == range(1, max_image_counter + 1))
def picture_present(message: Message) -> None:
    if message.text:
        bot.send_message(message.chat.id, 'Good, your request is accepted, now select your check in date',
                         reply_markup='')
        calendar_present(id=message.chat.id)
    # else:
    # bot.reply_to(message, 'Type error please try again.')
    # bot.register_next_step_handler(message, picture_present)


#   def low_price(message: Message) -> None:
#      name = message.text
#     UserInfoState.name = name
#    bot.send_message(message.from_user.id, f'{UserInfoState.name}, What city are you looking for an hotels?')
def calendar_present(id):
    calendar, step = MyStyleCalendar(locale='en', min_date=datetime.date.today()).build()
    bot.send_message(id, f"Select {LSTEP[step]}", reply_markup=calendar)


@bot.callback_query_handler(func=MyStyleCalendar.func())
def callback_calendar(call: CallbackQuery) -> None:
    result, key, step = MyStyleCalendar(locale='en', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Choose {LSTEP[step]}", call.message.chat.id, call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"You selected {result}", call.message.chat.id, call.message.message_id)
        #data_set[call.message.chat.id]['check_in'] = result.strftime('%Y.%m.%d')
        bot.send_message(chat_id=call.message.chat.id, text="How long do you stay?")
        bot.register_next_step_handler(call.message, check_out)


#@bot.message_handler(func=lambda message: message.text == range(1, 31 + 1))
#def check_out(message: Message) -> None:
    #if message.text:


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
