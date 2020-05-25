from collections import namedtuple
from typing import NamedTuple
from aiogram import types


class Buttons(NamedTuple):
    items: list
    order: list = []


CITY_BUTTONS = Buttons(items=['Москва', 'Санкт-Петербург'],
                       order=[2])
DEAL_TYPE_BUTTONS = Buttons(items=['Купить', 'Снять на год и более', 'Снять до года', 'Посуточная аренда'])
ROOMS_BUTTONS = Buttons(items=['Студии', '1-комнатные', '2-комнатные', '3-комнатные', '4-комнатные и более'],
                        order=[2, 2, 1])
APARTMENT_TYPE_BUTTONS = Buttons(items=['Новостройки', 'Вторичка', 'Все'],
                                 order=[2, 1])
PRICE_BUTTONS = dict(rent=Buttons(items=['До 20 000 руб', 'До 30 000 руб', 'До 50 000 руб']),
                     sale=Buttons(items=['До 5 000 000 руб', 'До 10 000 000 руб', 'До 15 000 000 руб']))


def build_replykeyboard(iterable):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(*iterable)
    return markup


def build_inlinekeyboard(buttons, row_width: int = 3):
    """
    :param buttons: list or Buttons object.
        If callback is different from the button name - list of tuples: ({button name}, {button callback data}).
    :param row_width: int.
    :return: types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup(row_width=row_width)

    if isinstance(buttons, Buttons):
        name_is_callback = True if not isinstance(buttons.items[0], (list, set)) else False
        accumulated = 0
        order = buttons.order if buttons.order else [1 for _ in range(len(buttons.items))]
        for n in order:
            if name_is_callback:
                inline_buttons = [types.InlineKeyboardButton(text=buttons.items[accumulated+i],
                                                             callback_data=buttons.items[accumulated+i])
                                  for i in range(n)]
            else:
                inline_buttons = [types.InlineKeyboardButton(text=buttons.items[accumulated+i][0],
                                                             callback_data=buttons.items[accumulated+i][1])
                                  for i in range(n)]
            markup.row(*inline_buttons)
            accumulated += n
    elif isinstance(buttons, list):
        name_is_callback = True if not isinstance(buttons[0], (list, set)) else False
        for button in buttons:
            if name_is_callback:
                markup.add(types.InlineKeyboardButton(text=button, callback_data=button))
            else:
                markup.add(types.InlineKeyboardButton(text=button[0], callback_data=button[1]))
    else:
        raise TypeError('Unknown type of buttons in app.buttons.build_inlinekeyboard')

    return markup


EMPTY_MARKUP = types.ReplyKeyboardRemove()
