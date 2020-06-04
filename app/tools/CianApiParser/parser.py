import json
import requests

from app.tools import proxy_processor


API = "https://api.cian.ru/search-engine/v1/search-offers-mobile-site/"


class ApiManager:
    def __init__(self):
        pass

    def get_data(self, json_query: dict) -> dict:
        response = requests.post(API, json=json_query)
        print("response code: ", response.status_code)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            raise ConnectionError


class QueryConstructor:
    def __init__(self,
                 region: list = None,
                 price: tuple = None,
                 room: list = None,
                 foot_min: int = None,
                 total_area: tuple = None,
                 living_area: tuple = None,
                 is_first_floor: bool = None,
                 not_last_floor: bool = None,
                 windows_type: int = None,
                 _type: str = None,  # TODO
                 floor: tuple = None,
                 is_by_homeowner: bool = None,
                 currency: int = 2,
                 engine_version: int = 2):
        """
        Args
            region (:list of int): Идентификатор региона (1 - Москва, 2 - Санкт-Петербург).
            price (:tuple of int): Диапазон цен.
            room (:list of int): Количество комнат (может быть несколько вариантов).
                Пример: [1,2,9] - 1к, 2к и студии.
            foot_min (:int): Количество минут пешком до ближайшего метро.
            total_area (:tuple int): Общая площадь (м2).
            living_area (:tuple of int): Жилая площать (от и до, м2).
            is_first_floor (:bool): Не первый ли этаж.
            not_last_floor (:bool): Не последний ли этаж.
            windows_type (:int): Вид из окна ().
            _type (:str): ??? ("flatsale").
            floor (:tuple of int): Диапазон допустимых этажей для поиска.
            is_by_homeowner (:bool): Предложение от собственника или нет.
            currency (:int): ??? (константа).
            engine_version (:int): (константа).
        """
        self.__currency = currency
        self.__engine_version = engine_version
        self.__region = region
        self.__price = price
        self.__room = room
        self.__foot_min = foot_min
        self.__total_area = total_area
        self.__living_area = living_area
        self.__is_first_floor = is_first_floor
        self.__not_last_floor = not_last_floor
        self.__windows_type = windows_type
        self.___type = _type
        self.__floor = floor
        self.__is_by_homeowner = is_by_homeowner

    @property
    def currency(self):
        return {'currency': {"type": "term", "value": self.__currency}}

    @property
    def engine_version(self):
        return {'engine_version': {"type": "term", "value": self.__engine_version}}

    @property
    def region(self):
        return {"region": {"type": "terms", "value": self.__region}}

    @property
    def price(self):
        return {"price": {"type": "range", "value": {"gte": self.__price[0], "lte": self.__price[1]}}}

    @property
    def room(self):
        return {'room': {"type": "terms", "value": self.__room}}

    @property
    def foot_min(self):
        return {
            {"only_foot": {"type": "term", "value": "2"}},
            {"foot_min": {"type": "range", "value": {"lte": self.__foot_min}}}
        }

    @property
    def total_area(self):
        return {"total_area": {"type": "range", "value": {"gte": self.__total_area[0], "lte": self.__total_area[1]}}}

    @property
    def living_area(self):
        return {'living_area': {"type": "range", "value": {"gte": self.__living_area[0], "lte": self.__living_area[1]}}}

    @property
    def is_first_floor(self):
        return {"is_first_floor": {"type": "term", "value": self.__is_first_floor}}

    @property
    def not_last_floor(self):
        return {"not_last_floor": {"type": "term", "value": self.__not_last_floor}}

    @property
    def windows_type(self):
        return {"windows_type": {"type": "term", "value": self.__windows_type}}

    @property
    def _type(self):
        return {'_type': self.___type}

    @property
    def floor(self):
        return {'floor':{"type": "range", "value": {"gte": self.__floor[0], "lte": self.__floor[1]}}}

    @property
    def is_by_homeowner(self):
        return {"is_by_homeowner": {"type": "term", "value": self.__is_by_homeowner}}




















