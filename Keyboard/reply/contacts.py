import json
import re
from typing import Optional, Union

import requests
from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from commans_to_requests import headers


def city_founding(city_name: str):
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


def hotel_founding(city_name: str):
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


def hotel_suggestions(city_name: str, city_id: str, quantity: str, data_in: str, data_out: str):
    querystring = {"query": city_name, "destinationId": city_id, "pageNumber": "1", "pageSize": quantity,
                   "checkIn": data_in, "checkOut": data_out,
                   "adults1": "1", "sortOrder": "PRICE", "id": "424023", "id": "1178275040", "currency": "USD",
                   "locale": "en_US"}
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/properties/list', headers=headers, params=querystring)
    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    find = re.search(pattern, response.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        hotel_properties = list()
        for dest_id in suggestions['results']:  # Обрабатываем результат
            hotel_compatibility = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['name'])
            hotel_properties.append({'name': hotel_compatibility, 'star_rate': dest_id['starRating'],
                                     'Address': dest_id['address']['streetAddress'],
                                     'city': dest_id['address']['locality'],
                                     'postal code': dest_id['address']['postalCode'],
                                     'distance from the center': dest_id['landmarks'][1]['distance'],
                                     'price': dest_id['ratePlan']['price']['exactCurrent']})
        hotel_properties_sorted = sorted(hotel_properties, key=lambda x: x['price'], reverse=False)
        user_request = hotel_properties_sorted[0:]
        # return hotel_properties
        return user_request


def city_markup(name: str) -> Optional[InlineKeyboardMarkup]:
    cities = city_founding(city_name=name)  # Функция "city_founding" уже возвращает список словарей с нужным именем и id
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data='city_' + city["destination_id"]))
    return destinations


def gen_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(text='Yes', callback_data='cb_yes'), InlineKeyboardButton(text='No',
                                                                                              callback_data='cb_no'))
    return markup


def hotel_markup(name: str, destination_id: str, number: str, check_in: str, check_out: str):
    hotels = hotel_suggestions(city_name=name, city_id=destination_id, quantity=number, data_in=check_in,
                               data_out=check_out)
    hotel_destination = InlineKeyboardMarkup()
    for hotel in hotels:
        hotel_destination.add(InlineKeyboardButton(text=hotel['name'],
                                                   callback_data=f'{hotel["price"]}'))
    return hotel_destination


def get_pictures(id_hotel: str) -> Union[list]:
    """Функция для запроса к API и получения данных о фотографиях"""
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
    except TypeError:
        print('Error')


def photos(id_hotel: str) -> Union[list]:
    """ Function for getting out photos etch hotel"""
    result = get_pictures(id_hotel=id_hotel)
    res = [i for i in list(zip(*result))[1]]
    return res

def picture_validation(picture: str) -> bool:
    """Функция для проверки URL фото"""
    try:
        s = requests.Session
        valid = s.get(url=picture, timeout=30)
        if valid.status_code == 200:
            return True
        return False
    except ConnectionError:
        return False


def request_contact() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Send contact', request_contact=True))
    return keyboard


def request_city(city: str) -> Union[bool, str]:
    """Функция для запроса к API и получения данных о городе"""
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city, "locale": "ru_RU", "currency": "RUB"}
    s = requests.Session()
    try:
        request = s.get(url=url, headers=headers, params=querystring)
        data = json.loads(request.text)
        coordinates = f'{data["suggestions"][0]["entities"][0]["latitude"]} + ' \
                      f'{data["suggestions"][0]["entities"][0]["longitude"]}'
        return f'{data["suggestions"][0]["entities"][0]["destinationId"]}|' \
               f'{data["suggestions"][0]["entities"][0]["name"]}|{coordinates}'
    except LookupError:
        return False


def parse_list(parse_list: list, uid: str, city: str, distance: str) -> Union[None, list]:
    """Функция для подготовки данных к записи в бд"""
    hotels = []
    hotel_id, name, adress, center, price = '', '', '', 'нет данных', ''

    for hotel in parse_list:
        try:
            hotel_id = hotel['id']
            name = hotel['name']
            adress = f'{hotel["address"]["countryName"]}, {city.capitalize()}, {hotel["address"].get("postalCode", "")}, {hotel["address"].get("streetAddress", "")}'
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

#parse_list(parse_list=data['data']['body']['searchResults']['results'], uid=list_param[5],
                          #  city=list_param[0], distance=list_param[9])
#print(parse_list(uid='1506246', city='london', distance='2.5'))
#print(photos(id_hotel='1178275040'))
#print(city_founding(city_name='london'))
#print(city_markup(name='london'))





#print(request_city(city='new  york'))
#print(hotel_suggestions('London, England, United Kingdom', '549499', '15', '2020-07-15', '2020-07-17'))
# print(hotel_suggestions(hotel='Prima'))
# print(hotel_markup())
#print(hotel_founding(city_name='Tel Aviv'))
#print(place_mach(city_name='Tel Aviv'))
#print(commute_junction(city_name='Tel Aviv'))
#https://github.com/inforeset/Hotels_bot/blob/master/price.py
