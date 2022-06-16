import telebot
from telebot import custom_filters
import Config_data
from telebot.custom_filters import StateFilter
from loader import bot
import Heandlers
from utils.set_bot_commands import set_default_commands


#default_commands = ['Start', 'Lets go', 'Help', 'Go out information', 'Survey', 'Get data']


if __name__ == '__main__':
    set_default_commands(bot)
    #bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.infinity_polling()



# def low_high_price(message) -> None:
# bot.set_state(message.from_user.id, Hotel_priceInfo.city, messagee.chat.id)



# response = requests.get('http://hotels.com/ho')
# response_1 = requests.get('https://www.breakingbadapi.com/api/death')
# data = json.loads(response.text)
# print(data)33
# data_1 = json.loads(response_1.text)
# with open('my_file.json', 'w') as file:
# json.dump(data, file, indent=4)
# print(data)

# sorted_data = sorted(data_1, key=lambda x: x['number_of_deaths'], reverse=True)
# print('\nпроизошло смертей - {} в {} эпизоде в {} сизоне'.format(sorted_data[0]['number_of_deaths'],
# sorted_data[0]['episode'],
# sorted_data[0]['season']))