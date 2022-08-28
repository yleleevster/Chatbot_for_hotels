import json
import re
from typing import Optional
from loguru import logger
from requests import RequestException, ReadTimeout
from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup, InputMediaPhoto)
from states.commans_to_requests import *


def request_city(city_name: str) -> list[dict[str, str]]:
    """
    Function for API requests and getting out data about cities
    :param city_name:
    :return: list of dictionaries contained strings of city names, destinationId and boolean
    """
    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": city_name.lower(), "locale": "en_US", "currency": "USD"}
    try:
        response = request_to_api(url=url, headers=headers, querystring=querystring)
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        find = re.search(pattern, response.text)
        if find:
            suggestions = json.loads(f"{{{find[0]}}}")
            cities = list()
            for dest_id in suggestions['entities']:  # Обрабатываем результат
                clear_destination = re.sub(r"<span class='highlighted'>|</span>", r'', dest_id['caption'])
                cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
            return cities
        else:
            logger.debug('Key error: "CITY_GROUP", no response from API')
    except (LookupError, ConnectionError, RequestException, ReadTimeout) as exc:
        logger.exception(exc)


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


def hotel_suggestions(city_id: str, quantity: str, sortorder: str) -> Union[list[dict[str, str]], bool]:
    """
    Function for request to API and getting out data about city id, user hotel quantity and sorting order
    according to command /lowprice and /highprice
    :param city_id:
    :param quantity:
    :param sortorder:
    :return:
    """
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": quantity,
                   "checkIn": '2020-01-08', "checkOut": '2020-01-15',
                   "adults1": "1", "sortOrder": sortorder, "currency": "USD",
                   "locale": "en_US"}
    try:
        response = request_to_api(url='https://hotels4.p.rapidapi.com/properties/list', headers=headers,
                                  querystring=querystring)
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
                    continue
            return hotel_properties
        else:
            logger.debug('The key does not exist')
    except (LookupError, ConnectionError, RequestException, ReadTimeout) as exc:
        logger.exception(exc)


def best_seller(city_id: str, quantity: str, min_price: str, max_price, distance: int) -> list[dict[str, str]]:
    """
    Function for request to API and getting out data about city id, user hotel quantity, minimal price, maximum price
     of hotels and distance from hotel's landmarks to the city center, according to command /bestdeal.
    :param city_id:
    :param quantity:
    :param min_price:
    :param max_price:
    :param distance:
    :return:
    """
    querystring = {"destinationId": city_id, "pageNumber": "1", "pageSize": quantity,
                   "checkIn": '2020-01-08', "checkOut": '2020-01-15',
                   "adults1": "1", "priceMin": min_price, "priceMax": max_price,
                   "sortOrder": 'DISTANCE_FROM_LANDMARK', "currency": "USD", "locale": "en_US",
                   "landmarkIds": 'City center'}
    try:
        response = request_to_api(url='https://hotels4.p.rapidapi.com/properties/list', headers=headers,
                                  querystring=querystring)
        pattern = r'(?<=,)"results":.+?(?=,"pagination)'
        find = re.search(pattern, response.text)
        if find:
            suggestions = json.loads(f"{{{find[0]}}}")
            bestdeal_compatibility = list()
            for i_key in suggestions['results']:  # Обрабатываем результат
                empty_dict = i_key["address"].get("streetAddress", "")
                # empty_price = i_key.get('ratePlan', {}).get('price', {}).get('exactCurrent', {})
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
            bestdeal_sorted = sorted(bestdeal_compatibility, key=lambda x: x['price'], reverse=False)
            return bestdeal_sorted
        else:
            logger.debug('The key does not exist')
    except (LookupError, ConnectionError, RequestException, ReadTimeout) as exc:
        logger.exception(exc)


def gen_markup() -> Optional[InlineKeyboardMarkup]:
    """
    Function that generate inline keyboard of answers: Yes/No
    :return:
    """
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='Yes', callback_data='cb_yes'), InlineKeyboardButton(text='No',
                                                                                              callback_data='cb_no'))
    return markup


def command_gen() -> Optional[InlineKeyboardMarkup]:
    """
    Function that generate inline keyboard made up commands - /lowprice, /highprice, /bestdeal and /history
    :return:
    """
    commands = ['/lowprice', '/highprice', '/bestdeal', '/history']
    key_board = InlineKeyboardMarkup(row_width=1)
    # btn = InlineKeyboardButton(text='Back', callback_data='MainMenu')
    r = [InlineKeyboardButton(text=x, callback_data=x) for x in commands]
    key_board.add(*r)
    return key_board


def get_pictures(id_hotel: str) -> list:
    """
    Function for request to API and getting data about pictures of the same hotel
    :param id_hotel:
    :return:
    """
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": id_hotel}
    pictures = []
    try:
        response = request_to_api(url=url, headers=headers, querystring=querystring)
        data = json.loads(response.text)
        for pic in data['hotelImages']:
            url = pic['baseUrl'].replace('_{size}', '_z')
            pictures.append((id_hotel, url))
        return pictures
    except (TypeError, KeyError, RequestException) as exc:
        logger.exception(exc)


def photos(id_hotel: str, quantity_photos=None) -> Union[str, list]:
    """
    Function for getting out photos from etch hotel according to user amount
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


def media_group_creation(pics: list) -> list:
    """
    Function for generation intermedia
    :param pics:
    :return:
    """
    pic_list = []
    for i in pics:
        pic_list.append(InputMediaPhoto(media=i))
    return pic_list


def picture_validation(picture: str) -> bool:
    """
    Function for cheking URL of the picture
    :param picture:
    :return:
    """
    try:
        valid = requests.get(url=picture, timeout=30)
        if valid.status_code == 200:
            return True
    except RequestException as exc:
        logger.exception(exc)
        return False


def request_contact() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(True, True)
    keyboard.add(KeyboardButton('Send contact', request_contact=True))
    return keyboard


def request_city_markup(name: str) -> Union[list[str], InlineKeyboardMarkup, bool]:
    """
    Function for generation inline keyboard made up different regions of the city
    :param name:
    :return:
    """
    cities = request_city(city_name=name)
    destinations = InlineKeyboardMarkup()
    if cities:
        for city in cities:
            destinations.add(
                InlineKeyboardButton(text=city['city_name'], callback_data='city_' + city["destination_id"]))
        if len(destinations.to_dict()['inline_keyboard']) == 0:
            logger.info('the city is not found')
        return destinations
    elif cities is None:
        return False
