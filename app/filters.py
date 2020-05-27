from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text


#search_terms = CallbackData('search_terms', 'type')
#search_terms_types = ['city', 'deal', 'rooms', 'apart_type', 'price']

#search_terms = Text(contains=['city', 'deal', 'rooms', 'apart_type', 'price'], ignore_case=False)


def search_terms(callback):
    return callback.data in ['city', 'deal', 'rooms', 'apart_type', 'price']

