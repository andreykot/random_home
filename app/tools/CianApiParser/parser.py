import json
from random import randint
import re
import requests

from app.tools import proxy_processor


API = "https://api.cian.ru/search-engine/v1/search-offers-mobile-site/"
FLATS_PER_PAGE = 28


class QueryConstructor:
    def __init__(self, page: int, region: list, type: str,
                 building_status: int = None,
                 price: list = None,
                 room: list = None,
                 underground_id: int = None,
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
            building_status (:int): Тип жилья. (новостройки - 2, вторичка - 1)
            price (:tuple of int): Диапазон цен.
            room (:list of int): Количество комнат (может быть несколько вариантов).
                Пример: [1,2,9] - 1к, 2к и студии.
            underground_id (:int): Кодовый номер станции метро согласно post-запросам ЦИАН.
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

        #self._geo = dict()
        #self._geo.update({'underground_id': None})

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

    def create_json_query(self):
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
            return {"for_day": {"type": "term", "value": "!1"}, '_type': 'flatrent'}
        elif self._type == 'flatrent_24h':
            return {"for_day": {"type": "term", "value": "1"}, '_type': 'flatrent'}
        else:
            raise ValueError

    @property
    def building_status(self):
        return {"building_status": {"type": "terms", "value": self._building_status}}

    @property
    def price(self):
        return {"price": {"type": "range", "value": {"gte": int(self._price[0]), "lte": int(self._price[1])}}}

    @property
    def room(self):
        return {'room': {"type": "terms", "value": self._room}}

    @property
    def geo(self):
        geo = {"geo": {"type": "geo", "value": []}}
        for key, item in self._geo.items():
            if key == 'underground_id' and self._geo['underground_id']:
                geo['geo']['value'].append({"type": "underground", "id": self._geo['underground_id']})

        return geo

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
        try:
            self.id: int = api_data['id']
            self.cian_id: int = api_data['cianId']
            self.price: int = api_data['price']['value']
            self.description: str = api_data['description']
            self.coordinates: dict = {'lat': api_data['geo']['coordinates']['lat'],
                                      'lng': api_data['geo']['coordinates']['lng']}
            self.phone: str = f"{api_data['phones'][0] if len(api_data['phones']) > 0 else ''}"

            self.__undergrounds: list = api_data['geo']['undergrounds']
            self.__info: dict = api_data['features']

        except (KeyError, IndexError):
            print(api_data)
            raise RuntimeError("Couldn't parse data of this flat.")

    @property
    def url(self) -> str:
        return f"https://cian.ru/sale/flat/{self.id}/"

    @property
    def address(self) -> dict:
        city, street, house = None, None, None
        for item in self.api_data['geo']['address']:
            if item['key'] == 'location':
                city = item['value']
            if item['key'] == 'street':
                street = item['value']
            if item['key'] == 'house':
                house = item['value']
        return {'city': city, 'street': street, 'house': house}

    @property
    def info(self) -> dict:
        info = dict()
        if 'floorInfo' in self.api_data['features']:
            info.update({'floor': self.api_data['features']['floorInfo']})
        if 'objectType' in self.api_data['features']:
            info.update({'object_type': self.api_data['features']['objectType']})
        if 'totalArea' in self.api_data['features']:
            info.update({'area': self.api_data['features']['totalArea'].replace(u'\xa0', ' ')})
        return info

    @property
    def underground(self) -> dict:
        if self.__undergrounds:
            nearest_by_transport, nearest_by_walk = (None, float('inf'), None), (None, float('inf'), None)
            for station in self.__undergrounds:
                raw_time = re.search(r'(\d+) (\w+)\.', station['time'].replace(u'\xa0', ' '))
                time, units = int(raw_time[1]), raw_time[2]

                if station['transportType'] == 'transport' and time < nearest_by_transport[1]:
                    nearest_by_transport = (station['name'], time, units)

                if station['transportType'] == 'walk' and time < nearest_by_walk[1]:
                    nearest_by_walk = (station['name'], time, units)

            if nearest_by_walk[0]:
                return {'name': nearest_by_walk[0],
                        'time': nearest_by_walk[1],
                        'units': nearest_by_walk[2],
                        'type': 'walk'}
            elif nearest_by_transport[0]:
                return {'name': nearest_by_transport[0],
                        'time': nearest_by_transport[1],
                        'units': nearest_by_transport[2],
                        'type': 'transport'}
            else:
                return {'name': None, 'time': None, 'units': None, 'type': None}
        else:
            return {'name': None, 'time': None, 'units': None, 'type': None}

    @property
    def underground_txt(self):
        data = self.underground
        if data['type'] == 'walk' and data['time']:
            return f"ст. {data['name']}, пешком {data['time']} {data['units']}"
        elif data['type'] == 'transport' and data['time']:
            return f"ст. {data['name']}, транспортом {data['time']} {data['units']}"
        elif data['type']:
            return f"ст. {data['name']}"
        else:
            return "не определено"


class ApiManager:
    def __init__(self, query: QueryConstructor):
        self.query = query
        self.data = None
        self.init()

    def init(self):
        json_query = json.dumps(self.query.create_json_query()).encode('utf8')
        response = proxy_processor.post_cian(json_query=json_query)
        response = requests.post(API, data=json_query)
        print(response.status_code)
        if response.status_code == 200:
            self.data = json.loads(response.content)
        else:
            raise RuntimeError

    def get_random_flat(self):
        n = randint(0, len(self.data['offers'])-1)
        if 'offers' in self.data:
            flat = CianFlat(api_data=self.data['offers'][n])
            return flat
        else:
            return None


if __name__ == '__main__':
    q = QueryConstructor(page=3, region=[2], type='flatsale')
    print(q.create_json_query())
    #data = ApiManager(query=q)
    #flat = data.data
    #print(flat)
    #print(flat.url,
    #      flat.address,
    #      flat.info,
    #     flat.underground)
    newConditions = {'jsonQuery': {'page': {'type': 'term', 'value': 3}, 'region': {'type': 'terms', 'value': [2]}, '_type': 'flatsale', 'currency': {'type': 'term', 'value': 2}, 'engine_version': {'type': 'term', 'value': 2}}}
    from urllib.request import Request, urlopen

    params = json.dumps(newConditions).encode('utf8')
    #req = Request(API, data=params, headers={'content-type': 'application/json'})
    req = requests.post(API, data=params)
    print(req.status_code)
    print(req.content)
    #response = urlopen(req)
    #print(response.read().decode('utf8'))

















