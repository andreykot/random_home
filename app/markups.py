from aiogram import types

from app.configs import bot_config


def build_from_list(iterable):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(*iterable)
    return markup


EMPTY_MARKUP = types.ReplyKeyboardRemove()
