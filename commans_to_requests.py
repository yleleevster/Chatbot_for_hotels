import json
import re
from telebot import logger

import requests

from keyboard.reply.contacts import parse_list

headers = {"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
           "X-RapidAPI-Key": "77491f4edfmshfb1c9b48fd4a1bbp18a4f7jsn64125fb29511"}


querystring = {"query": "new york", "destinationId": "1506246", "pageNumber": "1", "pageSize": "25",
               "checkIn": "2020-01-08", "checkOut": "2020-01-15",
               "adults1": "1", "sortOrder": "PRICE", "currency": "USD",
               "locale": "en_US"}


def request_to_api(url, pattern):
    try:
        s = requests.Session()
        response = s.get(url=url, headers=headers, params=querystring)
        patt = pattern
        find = re.search(patt, response.text)
        if find:
            data_1 = json.loads(f'{{{find[0]}}}')
            with open('file.json', 'w', encoding='utf-8') as file:
                json.dump(data_1, file, indent=4)
                file.write(str(data_1))
        else:
            return 'The key does not exist'
        if response.status_code == requests.codes.ok:
            return response.text
    except ConnectionError:
        print('No response')


def collect_data():
    s = requests.Session()
    response = s.get(url='https://hotels4.p.rapidapi.com/properties/list', headers=headers, params=querystring)
    data = response.text
    id_count = data.find('results')
    result_i = []
    for i in range(1, id_count + 1):
        url = f'https://ru.hotels.com/ho{hotel_id}'
        r = s.get(url=url, headers=headers, params=querystring)
        data = r.text
        id_num = data.find('id')
        for j in range(id_num):
            res = j
            print(res)


#result = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="CITY_GROUP",).+?[\]]')
#result_1 = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="HOTEL_GROUP",).+?[\]]')
#result_2 = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="LANDMARK_GROUP",).+?[\]]')
#result_3 = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="TRANSPORT_GROUP",).+?[\]]')

#result1 = request_to_api('https://hotels4.p.rapidapi.com/properties/list',
                         #r'(?<=,)"results":.+?(?=,"pagination)')

def request_list(id: str, list_param: list) -> list:
    """Function for requests to API and getting basic data"""
    url = "https://hotels4.p.rapidapi.com/properties/list"
    checkIn = '-'.join(list_param[1].split('.')[::-1])
    checkOut = '-'.join(list_param[2].split('.')[::-1])
    sortOrder = ''
    landmarkIds = ''
    priceMin = ''
    priceMax = ''
    pageSize = list_param[4]
    if list_param[6] == '/lowprice':
        sortOrder = 'PRICE'
    elif list_param[6] == '/highprice':
        sortOrder = 'PRICE_HIGHEST_FIRST'
    elif list_param[6] == '/bestdeal':
        sortOrder = 'DISTANCE_FROM_LANDMARK'
        landmarkIds = 'Центр города'
        priceMin = list_param[7]
        priceMax = list_param[8]

    querystring = {"destinationId": id, "pageNumber": "1", "pageSize": pageSize, "checkIn": checkIn,
                   "checkOut": checkOut, "adults1": "1", "priceMin": priceMin, "priceMax": priceMax,
                   "sortOrder": sortOrder, "locale": "ru_RU", "currency": "RUB",
                   "landmarkIds": landmarkIds}
    try:
        request = requests.get(url=url, headers=headers, params=querystring)
        data_set = json.loads(request.text)
        parsed_data = parse_list(parse_list=data_set['data']['body']['searchResults']['results'], uid=list_param[5],
                                 city=list_param[0], distance=list_param[9])
        return parsed_data
    except (LookupError, TypeError) as exc:
        logger.exception(exc)