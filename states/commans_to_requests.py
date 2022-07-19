from typing import Union
import requests
from requests import Response
from telebot import logger

from config_data.config import rapid_api_key

headers = {"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
           "X-RapidAPI-Key": rapid_api_key}


def request_to_api(url, headers, querystring) -> Union[Response, bool]:
    try:
        s = requests.Session()
        response = s.get(url, headers=headers, params=querystring, timeout=30)
        if response.status_code == requests.codes.ok:
            return response
    except requests.exceptions.RequestException as exc:
        logger.info('No response because of {}'.format(exc))
        return False
