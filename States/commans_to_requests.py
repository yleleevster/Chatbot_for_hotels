import requests
import re
import json

from Config_data.config import rapid_api_key

headers = {"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
           "X-RapidAPI-Key": rapid_api_key}

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


result = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="CITY_GROUP",).+?[\]]')
#result_1 = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="HOTEL_GROUP",).+?[\]]')
#result_2 = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="LANDMARK_GROUP",).+?[\]]')
#result_3 = request_to_api('https://hotels4.p.rapidapi.com/locations/v2/search', r'(?<="TRANSPORT_GROUP",).+?[\]]')

#result1 = request_to_api('https://hotels4.p.rapidapi.com/properties/list',
                         #r'(?<=,)"results":.+?(?=,"pagination)')
# collect_data()
# data_1 = json.loads(response_1.text)
# with open('my_file.json', 'w') as file:
# json.dump(data, file, indent=4)
# print(data)