import json
import re
from typing import Optional, Union
from loguru import logger
import requests
from states.contact_info import *
from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from states.commans_to_requests import headers


def city_founding(city_name: str) -> list:
    querystring = {"query": city_name.lower(), "locale": "en_US", "currency": "USD"}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/locations/v2/search', headers=headers, params=querystring)
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        cities = list()
        for dest_id in suggestions['entities']:  # Обрабатываем результат
            clear_destination = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['caption'])
            cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
        return cities


def hotel_founding(city_name: str) -> list:
    querystring = {"query": city_name.lower(), "locale": "en_US", "currency": "USD"}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/locations/v2/search', headers=headers, params=querystring)
    pattern = r'(?<="HOTEL_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        hotels = list()
        for dest_id in suggestions['entities']:  # Обрабатываем результат
            clear_destination = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['caption'])
            hotels.append({'hotel_name': clear_destination, 'destination_id': dest_id['destinationId']})
        return hotels


def place_mach(city_name):
    querystring = {"query": city_name.lower(), "locale": "en_US", "currency": "USD"}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/locations/v2/search', headers=headers, params=querystring)
    pattern = r'(?<="LANDMARK_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        places = list()
        for dest_id in suggestions['entities']:  # Обрабатываем результат
            clear_destination = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['caption'])
            places.append({'place': clear_destination, 'destination_id': dest_id['destinationId']})
        return places


def commute_junction(city_name: str):
    querystring = {"query": city_name.lower(), "locale": "en_US", "currency": "USD"}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/locations/v2/search', headers=headers, params=querystring)
    pattern = r'(?<="TRANSPORT_GROUP",).+?[\]]'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        public_transport = list()
        for dest_id in suggestions['entities']:  # Обрабатываем результат
            clear_destination = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['caption'])
            commute_transport = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['type'])
            public_transport.append({'transport': commute_transport,
                                     'station': clear_destination, 'destination_id': dest_id['destinationId']})
        return public_transport


def hotel_suggestions(city_id: str, quantity: str, ) -> list[dict[str, str]]:
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": quantity,
                   "checkIn": '2020-01-08', "checkOut": '2020-01-15',
                   "adults1": "1", "sortOrder": "PRICE", "currency": "USD",
                   "locale": "en_US"}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/properties/list', headers=headers, params=querystring)
    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        hotel_properties = list()
        for dest_id in suggestions['results']:  # Обрабатываем результат
            empty_dict = dest_id["address"].get("streetAddress", "")
            try:
                hotel_compatibility = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['name'])
                hotel_properties.append({'id_hotel': dest_id['id'], 'name': hotel_compatibility,
                                         'star_rate': dest_id['starRating'],
                                         'Address': empty_dict,
                                         'city': dest_id['address']['locality'],
                                         'distance from the center': dest_id['landmarks'][0]['distance'],
                                         'price': dest_id['ratePlan']['price']['exactCurrent'],
                                         'link': f'https://exp.cdn-hotels.com/ho{dest_id["id"]}'})
            except (KeyError, IndexError) as exc:
                logger.exception(exc)
        hotel_properties_sorted = sorted(hotel_properties, key=lambda x: x['price'], reverse=False)
        user_request = hotel_properties_sorted[0:]
        # return hotel_properties
        return user_request


def hotel_suggestions_highest(city_id: str, quantity: str) -> list[dict[str, str]]:
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": quantity,
                   "checkIn": '2020-01-08', "checkOut": '2020-01-15',
                   "adults1": "1", "sortOrder": "PRICE_HIGHEST_FIRST", "currency": "USD",
                   "locale": "en_US"}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/properties/list', headers=headers, params=querystring)
    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        hotel_properties = list()
        for dest_id in suggestions['results']:  # Обрабатываем результат
            empty_dict = dest_id["address"].get("streetAddress", "")
            try:
                hotel_compatibility = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['name'])
                hotel_properties.append({'id_hotel': dest_id['id'], 'name': hotel_compatibility,
                                         'star_rate': dest_id['starRating'],
                                         'Address': empty_dict,
                                         'city': dest_id['address']['locality'],
                                         'distance from the center': dest_id['landmarks'][0]['distance'],
                                         'price': dest_id['ratePlan']['price']['exactCurrent'],
                                         'link': f'https://exp.cdn-hotels.com/ho{dest_id["id"]}'})
            except (KeyError, IndexError):
                continue
        hotel_properties_sorted = sorted(hotel_properties, key=lambda x: x['price'], reverse=True)
        user_request = hotel_properties_sorted[0:]
        # return hotel_properties
        return user_request


# 0528626382
def best_seller(city_id: str, quantity: str, min_price: str, max_price, distance: int) -> list[dict[str, str]]:
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": quantity,
                   "checkIn": '2020-01-08', "checkOut": '2020-01-15',
                   "adults1": "1", "priceMin": min_price, "priceMax": max_price,
                   "sortOrder": 'DISTANCE_FROM_LANDMARK', "currency": "USD", "locale": "en_US",
                   "landmarkIds": 'City center'}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/properties/list', headers=headers, params=querystring)
    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        bestdeal_compatibility = list()
        for i_key in suggestions['results']:  # Обрабатываем результат
            empty_dict = i_key["address"].get("streetAddress", "")
            try:
                hotel_comp = re.sub(r"<span class='highlighted'>|</span>", r'', i_key['name'])
                if float(distance) > float(i_key["landmarks"][0]["distance"].split()[0].replace(',', '.')):
                    bestdeal_compatibility.append({'id_hotel': i_key['id'], 'name': hotel_comp,
                                                   'star_rate': i_key['starRating'],
                                                   'Address': empty_dict,
                                                   'city': i_key['address']['locality'],
                                                   'distance from the center': i_key['landmarks'][0]['distance'],
                                                   'price': i_key['ratePlan']['price']['exactCurrent'],
                                                   'link': f'https://exp.cdn-hotels.com/ho{i_key["id"]}'})
            except (KeyError, IndexError) as exc:
                logger.exception(exc)
                continue
        # return bestdeal_compatibility
        bestdeal_sorted = sorted(bestdeal_compatibility, key=lambda x: x['price'], reverse=False)
        return bestdeal_sorted


def distance_calculation(city_id: str, quantity: str, price_min: str, price_max: str, distance: int) -> list[dict]:
    res = best_seller(city_id=city_id, quantity=quantity, price_min=price_min, price_max=price_max, distance=distance)
    my_list = []
    for i in res:
        for key, value in i.items():
            try:
                if float(distance) > float(i.get('distance from the center').split()[0].replace(',', '.')):
                    my_list.append({key: value})
            except (LookupError, KeyError) as exc:
                logger.exception(exc)
    return my_list

    # return distance_sorted[0:]


def city_markup(name: str) -> Optional[InlineKeyboardMarkup]:
    cities = city_founding(city_name=name)  # Функция "city_founding" уже возвращает список словарей с нужным именем и id
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data='city_' + city["destination_id"]))
    return destinations


def gen_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='Yes', callback_data='cb_yes'), InlineKeyboardButton(text='No',
                                                                                              callback_data='cb_no'))
    return markup


def hotel_markup(name: str):
    hotels = hotel_suggestions(user)
    hotel_destination = InlineKeyboardMarkup()
    for hotel in hotels:
        hotel_destination.add(InlineKeyboardButton(text=hotel['name'],
                                                   callback_data='price_' + hotel["price"]))
    return hotel_destination


def get_pictures(id_hotel: str) -> Union[list]:
    """
    Function for request to API and getting data about pictures
    :param id_hotel:
    :return:
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": id_hotel}
    pictures = []
    try:
        s = requests.Session()
        response = s.get(url, headers=headers, params=querystring)
        data = json.loads(response.text)
        for pic in data['hotelImages']:
            url = pic['baseUrl'].replace('_{size}', '_z')
            pictures.append((id_hotel, url))
        return pictures
    except (TypeError, KeyError) as exc:
        logger.exception(exc)


def photos(id_hotel: str, quantity_photos=None):
    """
    Function for getting out photos from etch hotel
    :param id_hotel:
    :param quantity_photos:
    :return:
    """
    if quantity_photos is None:
        result = get_pictures(id_hotel=id_hotel)
        res = [i[0] for i in result]
        for i in res:
            return i
    else:
        result = get_pictures(id_hotel=id_hotel)
        res = [i for i in list(zip(*result))[1]]
        return res[0:int(quantity_photos)]


def picture_validation(picture: str) -> bool:
    """Функция для проверки URL фото"""
    try:
        s = requests.Session
        valid = s.get(url=picture, timeout=30)
        if valid.status_code == 200:
            return True
        return False
    except ConnectionError as exc:
        logger.exception(exc)
        return False


def request_contact() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Send contact', request_contact=True))
    return keyboard


def request_city(user):
    """Функция для запроса к API и получения данных о городе"""
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": user.city.lower(), "locale": "en_US", "currency": "USD"}
    s = requests.Session()
    response = s.get(url, headers=headers, params=querystring)
    try:
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        find = re.search(pattern, response.text)
        if find:
            suggestions = json.loads(f"{{{find[0]}}}")
            cities = list()
            for dest_id in suggestions['entities']:  # Обрабатываем результат
                clear_destination = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['caption'])
                cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
            return cities
    except LookupError as exc:
        logger.exception(exc)
        return False


def request_city_markup(user) -> Optional[InlineKeyboardMarkup]:
    cities = request_city(user)  # Функция "city_founding" уже возвращает список словарей с нужным именем и id
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data='city_' + city["destination_id"]))
    return destinations


# f'{data["suggestions"][0]["entities"][0]["name"]}|{coordinates}'

def parse_list(parse_list: list, uid: str, city: str, distance: str) -> Union[None, list]:
    """Функция для подготовки данных к записи в бд"""
    hotels = []
    hotel_id, name, adress, center, price = '', '', '', 'нет данных', ''

    for hotel in parse_list:
        try:
            hotel_id = hotel['id']
            name = hotel['name']
            adress = f'{hotel["address"]["countryName"]}, {city.capitalize()}, ' \
                     f'{hotel["address"].get("postalCode", "")}, {hotel["address"].get("streetAddress", "")}'
            if len(hotel['landmarks']) > 0:
                if hotel['landmarks'][0]['label'] == 'Центр города':
                    center = hotel['landmarks'][0]['distance']
            price = str(hotel['ratePlan']['price']['exactCurrent'])
            coordinates = f"{hotel['coordinate'].get('lat', 0)},{hotel['coordinate'].get('lon', 0)}"
            star_rating = str(hotel['starRating'])
            user_rating = hotel.get('guestReviews', {}).get('rating', 'нет данных').replace(',', '.')
            if distance != '':
                if float(distance) < float(center.split()[0].replace(',', '.')):
                    return hotels
            hotels.append((uid, hotel_id, name, adress, center, price, coordinates, star_rating, user_rating))
        except (LookupError, ValueError):
            continue
    return hotels


# parse_list(parse_list=data['data']['body']['searchResults']['results'], uid=list_param[5],
#  city=list_param[0], distance=list_param[9])
# print(parse_list(uid='1506246', city='london', distance='2.5'))
# print(get_pictures(id_hotel='564864'))

#print(city_founding(user))
#print(city_markup(name='london'))
#for i in city_markup(name='london').keyboard:
    #for j in i:
        #print(j)
# print(distance_calculation(city_id='10874216', quantity='6', price_min='40', price_max='300', distance=10))
#user.city = 'milan'
#user.destinationId = '712492'
#user.min_price = '300'
#user.max_price = '1000'
#user.distance = 3
#user.quantity_count = 3
#print(request_city(user))
#print(best_seller(city_id=user.destinationId, quantity=str(user.quantity_count), min_price=user.min_price, max_price=
                  #user.max_price, distance=user.distance))
#for i in photos(id_hotel='220590', quantity_photos=None):
    #print(i)
# print(hotel_suggestions_highest(city_id='10874216', quantity='4'))

#print(hotel_suggestions(user))
# for i in hotel_suggestions('1644891', '9'):
# for j, k in i.items():
# print(j, ':', k)
# for i in hotel_markup('london').keyboard:

# print(hotel_founding(city_name='Tel Aviv'))
# print(place_mach(city_name='Tel Aviv'))
# print(commute_junction(city_name='Tel Aviv'))
# https://github.com/inforeset/Hotels_bot/blob/master/price.py
