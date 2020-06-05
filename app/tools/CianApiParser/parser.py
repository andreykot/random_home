import json
import re
import requests

from app.tools import proxy_processor


API = "https://api.cian.ru/search-engine/v1/search-offers-mobile-site/"


class ApiManager:
    def __init__(self):
        pass

    @classmethod
    def get_data(cls, json_query: dict) -> dict:
        response = requests.post(API, json=json_query)
        print("response code: ", response.status_code)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            raise ConnectionError


class QueryConstructor:
    def __init__(self, page: int, region: list, type: str,
                 building_status: int = None,
                 price: tuple = None,
                 room: list = None,
                 foot_min: int = None,
                 total_area: tuple = None,
                 living_area: tuple = None,
                 is_first_floor: bool = None,
                 not_last_floor: bool = None,
                 windows_type: int = None,
                 floor: tuple = None,
                 is_by_homeowner: bool = None,
                 currency: int = 2,
                 engine_version: int = 2):
        """
        Args
            page (:int): Номер страницы.
            region (:list of int): Идентификатор региона (1 - Москва, 2 - Санкт-Петербург).
            type (:str): Тип предложения ('flatsale', 'flatrent', 'flatrent_24h').
            building_status (:int): Тип жилья.
            price (:tuple of int): Диапазон цен.
            room (:list of int): Количество комнат (может быть несколько вариантов).
                Пример: [1,2,9] - 1к, 2к и студии.
            foot_min (:int): Количество минут пешком до ближайшего метро.
            total_area (:tuple int): Общая площадь (м2).
            living_area (:tuple of int): Жилая площать (от и до, м2).
            is_first_floor (:bool): Не первый ли этаж.
            not_last_floor (:bool): Не последний ли этаж.
            windows_type (:int): Вид из окна ().
            floor (:tuple of int): Диапазон допустимых этажей для поиска.
            is_by_homeowner (:bool): Предложение от собственника или нет.
            currency (:int): ??? (константа).
            engine_version (:int): (константа).
        """
        self._page = page
        self._region = region
        self._type = type
        self._building_status = building_status
        self._price = price
        self._room = room
        self._foot_min = foot_min
        self._total_area = total_area
        self._living_area = living_area
        self._is_first_floor = is_first_floor
        self._not_last_floor = not_last_floor
        self._windows_type = windows_type
        self._floor = floor
        self._is_by_homeowner = is_by_homeowner
        self._currency = currency
        self._engine_version = engine_version

    def create(self):
        args = dict()
        for attr, value in self.__dict__.items():
            if value:
                args.update(getattr(self, attr[1:]))
        return {"jsonQuery": args}

    @property
    def page(self):
        return {'page': {"type": "term", "value": self._page}}

    @property
    def region(self):
        return {"region": {"type": "terms", "value": self._region}}

    @property
    def type(self):
        if self._type == 'flatsale':
            return {'_type': 'flatsale'}
        elif self._type == 'flatrent':
            return {'_type': 'flatrent', "for_day": {"type": "terms", "value": "!1"}}
        elif self._type == 'flatrent_24h':
            return {'_type': 'flatrent', "for_day": {"type": "terms", "value": "1"}}
        else:
            raise ValueError

    @property
    def building_status(self):
        return {"building_status": {"type": "terms", "value": self._building_status}}

    @property
    def price(self):
        return {"price": {"type": "range", "value": {"gte": self._price[0], "lte": self._price[1]}}}

    @property
    def room(self):
        return {'room': {"type": "terms", "value": self._room}}

    @property
    def foot_min(self):
        return {"only_foot": {"type": "term", "value": "2"}, "foot_min": {"type": "range", "value": {"lte": self._foot_min}}}

    @property
    def total_area(self):
        return {"total_area": {"type": "range", "value": {"gte": self._total_area[0], "lte": self._total_area[1]}}}

    @property
    def living_area(self):
        return {'living_area': {"type": "range", "value": {"gte": self._living_area[0], "lte": self._living_area[1]}}}

    @property
    def is_first_floor(self):
        return {"is_first_floor": {"type": "term", "value": self._is_first_floor}}

    @property
    def not_last_floor(self):
        return {"not_last_floor": {"type": "term", "value": self._not_last_floor}}

    @property
    def windows_type(self):
        return {"windows_type": {"type": "term", "value": self._windows_type}}

    @property
    def floor(self):
        return {'floor':{"type": "range", "value": {"gte": self._floor[0], "lte": self._floor[1]}}}

    @property
    def is_by_homeowner(self):
        return {"is_by_homeowner": {"type": "term", "value": self._is_by_homeowner}}

    @property
    def currency(self):
        return {'currency': {"type": "term", "value": self._currency}}

    @property
    def engine_version(self):
        return {'engine_version': {"type": "term", "value": self._engine_version}}


class CianFlat:
    def __init__(self, api_data: dict):
        self.api_data = api_data

        self.id: int = api_data['id']
        self.price: int = api_data['price']['value']
        self.description: str = api_data['description']
        self.address: str = \
            f"{api_data['geo']['address'][0]}, {api_data['geo']['address'][1]} {api_data['geo']['address'][2]}"
        self.coordinates: tuple = (api_data['geo']['coordinates']['lat'], api_data['geo']['coordinates']['lng'])

        self.__undergrounds = api_data['geo']['undergrounds']
        self.__info = api_data['features']

    @property
    def url(self):
        return f"https://cian.ru/sale/flat/{self.id}/"

    @property
    def info(self):
        return "{}, {}, {}".format(self.__info['floorInfo'],
                                   self.__info['objectType'],
                                   self.__info['totalArea'].replace(u'\xa0', ' '))

    @property
    def underground(self):
        if self.__undergrounds:
            nearest_by_transport, nearest_by_walk = (None, float('inf')), (None, float('inf'))
            for station in self.__undergrounds:
                timestr = station['time'].replace(u'\xa0', ' ')
                time = int(re.search(r'\d+', timestr)[0])

                if station['transportType'] == 'transport' and time < nearest_by_transport[1]:
                    text = f"Транспортом до ст. {station['name']} - {timestr}"
                    nearest_by_transport = (text, time)

                if station['transportType'] == 'walk' and time < nearest_by_walk[1]:
                    text = f"Пешком до ст. {station['name']} - {timestr}"
                    nearest_by_walk = (text, time)

            return  nearest_by_transport, nearest_by_walk
        else:
            raise ValueError('attr _undergrounds is empty.')


if __name__ == '__main__':
    q = QueryConstructor(page=3, region=[2], type='flatsale')
    args = q.create()
    data = ApiManager.get_data(json_query=args)
    print(data.keys())

















