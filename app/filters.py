from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text

from app import buttons


# callback filters

def search_terms(callback):
    return callback.data in ['city', 'deal', 'underground', 'rooms', 'apart_type', 'price']


# data filters

def city_filter(data):
    voc = {'Москва': 1,
           'Санкт-Петербург': 2}
    if data in voc:
        return [voc[data]]
    else:
        raise ValueError("Invalid city value.")


def deal_filter(data):
    voc = {'Купить': 'flatsale',
           'Снять': 'flatrent',
           'Посуточная аренда': 'flatrent_24h'}
    if data in voc:
        return voc[data]
    else:
        raise ValueError("Invalid deal value.")


def metro_line_filter(data):
    voc = {'Красная': 1, 'Синяя': 2, 'Зеленая': 3, 'Оранжевая': 4, 'Фиолетовая': 5}
    if data in voc:
        return voc[data]


underground_voc = {
        'Красная': {
            "Девяткино": 167,
            "Гражданский проспект": 168,
            "Академическая": 169,
            "Политехническая": 170,
            "Пл. Мужества": 171,
            "Лесная": 172,
            "Выборгская": 173,
            "Пл. Ленина": 174,
            "Чернышевская": 175,
            "Пл. Восстания": 176,
            "Владимирская": 177,
            "Пушкинская": 178,
            "Технологический институт": 179,
            "Балтийская": 180,
            "Нарвская": 181,
            "Кировский завод": 182,
            "Автово": 183,
            "Ленинский проспект": 184,
            "Проспект Ветеранов": 185},
        'Синяя': {
            "Парнас": 186,
            "Проспект Просвещения": 187,
            "Озерки": 188,
            "Удельная": 189,
            "Пионерская": 190,
            "Черная речка": 191,
            "Петроградская": 192,
            "Горьковская": 193,
            "Невский проспект": 194,
            "Сенная площадь": 195,
            "Технолический институт": 196,
            "Фрунзенская": 197,
            "Московский ворота": 198,
            "Электросила": 199,
            "Парк Победы": 200,
            "Московская": 201,
            "Звездная": 202,
            "Купчино": 203
        },
        'Зеленая': {
            "Беговая": 355,
            "Новокрестовская": 356,
            "Приморская": 204,
            "Василеостровская": 205,
            "Гостиный двор": 206,
            "Маяковская": 207,
            "Пл. Александра Невского": 208,
            "Елизаровская": 210,
            "Ломоносовская": 211,
            "Пролетарская": 212,
            "Обухово": 213,
            "Рыбацкое": 214
        },
        'Фиолетовая': {
            "Комендантский проспект": 215,
            "Старая деревня": 216,
            "Крестовский остров": 217,
            "Чкаловская": 218,
            "Спортивная": 219,
            "Адмиралтейская": 242,
            "Садовая": 220,
            "Звенигородская": 231,
            "Обводный канал": 241,
            "Волковская": 230,
            "Бухаресткая": 247,
            "Международная": 246,
            "Проспект Славы": 357,
            "Дунайская": 358,
            "Шушары": 359
        },
        'Оранжевая': {
            "Спасская": 232,
            "Достоевская": 221,
            "Лиговский проспект": 222,
            "Пл. Александра Невского": 208,
            "Новочеркасская": 224,
            "Ладожская": 225,
            "Проспект Большевиков": 226,
            "Улица Дыбенко": 227
        }
    }


def underground_station_filter(line: str, name: str):
    if (line in underground_voc) and (name in underground_voc[line]):
        return underground_voc[line][name]


def rooms_filter(data, mode):
    if mode == 'to_int':
        to_int = {'Студии': [9],
                  '1-комнатные': [1],
                  '2-комнатные': [2],
                  '3-комнатные': [3],
                  '4-комнатные и более': [4, 5, 6]}
        if data in to_int:
            return [*to_int[data]]
        else:
            raise ValueError("Invalid rooms value.")

    elif mode == 'array_to_str':
        array_to_str = {9: 'студии', 1: '1к', 2: '2к', 3: '3к', 4: '4к+'}
        result = [array_to_str[item] for item in data if item in array_to_str]
        return ', '.join(result) if result else ''

    else:
        raise TypeError('Unknown mode of filter.')


def apartment_type_filter(data):
    voc = {'Все': None, 'Новостройки': 2, 'Вторичка': 1}
    if data in voc:
        return voc[data]
    else:
        raise TypeError("Unsupported apartment type.")


def price_filter(data):
    rent_prices = dict(list(zip(buttons.PRICE['rent'].items, [(0, 20000), (0, 30000), (0, 50000)])))
    sale_prices = dict(list(zip(buttons.PRICE['sale'].items, [(0, 5000000), (0, 10000000), (0, 15000000)])))

    if data in rent_prices:
        return rent_prices[data]
    elif data in sale_prices:
        return sale_prices[data]
    else:
        raise TypeError("Unsupported price.")


# callback data

map = CallbackData('coordinates', 'lat', 'lng')

