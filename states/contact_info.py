from enum import Enum
from telebot.handler_backends import State, StatesGroup

max_hotel_counter = 10
max_image_counter = 5


class Users:
    """
    Class that represent user's parameters according to chatbot scenario
    all_users: dictionary for data storage
    Args:
        user_id (int): user identificator of chatbot
    """
    all_users = dict()
    # all_users = list()

    def __init__(self, user_id):
        self.user_id = user_id
        self.datetime = ''
        self.city = ''
        self.destinationId = ''
        self.quantity_count = ''
        self.image_input = ''
        self.image_exit = ''
        self.check_in = ''
        self.check_out = ''
        self.hotels_count = ''
        self.command = ''
        self.min_price = ''
        self.max_price = ''
        self.distance = 0
        Users.add_user(user_id, self)
        # Users.all_users.append(self)

    def __str__(self):
        return f"{self.user_id}, '{self.datetime}', '{self.city}', '{self.destinationId}', '{self.quantity_count}', " \
               f"'{self.hotels_count}', '{self.command}', '{self.min_price}', '{self.max_price}', '{self.distance}'," \
               f"'{self.image_input}', '{self.image_exit}', '{self.check_in}', '{self.check_out}'."

    @staticmethod
    def get_user(user_id):
        """
        Getter that return user's values of dictionary and instance class in absence of values
        :param user_id: (int)
        :return: new_user, Users.all_users.get(user_id)
        """
        if Users.all_users.get(user_id) is None:
            new_user = Users(user_id)
            return new_user
        return Users.all_users.get(user_id)

    @classmethod
    def add_user(cls, user_id, user):
        cls.all_users[user_id] = user
        # return cls.all_users
        # for user in cls.all_users:
        # print(user)


# class Requests(Users):
# def __init__(self, user_id, datetime):
# super().__init__(user_id)


user = Users.get_user(111)  # добавили пользователя
# user.command = 'high price' # Присвоили ввод команды

# print(user)
# В последующем вытаскиваем пользователя
# user = Users.get_user(111)
# user.city = 'london' # Добавляем новую информацию к объекту
