from enum import Enum

from telebot.handler_backends import State, StatesGroup

max_hotel_counter = 10
max_image_counter = 5


class UserInfoState(StatesGroup):
    name = State()
    surname = State()
    age = State()
    country = State()
    city = State()
    cellphone = State()


class States(Enum):
    start = "0"  # Начало нового диалога
    city = "1"
    quantity_count = "2"
    check_in = "3"
    check_out = "4"
    image_input = "5"
    image_quantity = "6"
    min_price = "7"
    max_price = "8"
    distance = "9"
