from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text

from app import buttons


# callback filters

def search_terms(callback):
    return callback.data in ['city', 'deal', 'rooms', 'apart_type', 'price']


# data filters

def deal_filter(data):
    voc = {'Купить': 1, 'Снять на год и более': 2, 'Снять до года': 3, 'Посуточная аренда': 4}
    if data in voc:
        return voc[data]
    else:
        raise ValueError("Invalid deal value.")


def rooms_filter(data, mode):
    if mode == 'to_int':
        to_int = {'Студии': 0, '1-комнатные': 1, '2-комнатные': 2, '3-комнатные': 3, '4-комнатные и более': 4}
        if data in to_int:
            return to_int[data]
        else:
            raise ValueError("Invalid rooms value.")

    elif mode == 'array_to_str':
        array_to_str = {0: 'студии', 1: '1к', 2: '2к', 3: '3к', 4: '4к+'}
        result = [array_to_str[item] for item in data if item in array_to_str]
        if len(data) != len(result):
            raise ValueError("Invalid rooms value.")

        return ', '.join(result) if result else ''

    else:
        raise TypeError('Unknown mode of filter.')


def apartment_type_filter(data):
    voc = {'Все': 0, 'Новостройки': 1, 'Вторичка': 2}
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

