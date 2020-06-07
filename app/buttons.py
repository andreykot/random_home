from typing import NamedTuple
from random import randint
from aiogram import types


class Buttons(NamedTuple):
    items: list
    order: list = []

    def __repr__(self):
        return "items: {}, order: {}".format(self.items, self.order)


START_SEARCH = Buttons(items=['Задать критерии поиска'])
SEARCH_TERMS = Buttons(
    items=[('Выбрать город', 'city'),
           ('Тип предложения: купить или снять?', 'deal'),
           ('Задать количество комнат', 'rooms'),
           ('Новостройка или вторичка?', 'apart_type'),
           ('Задать ценовой диапазон', 'price')]
                       )

CITY = Buttons(items=['Москва', 'Санкт-Петербург'], order=[2])
DEAL_TYPE = Buttons(items=['Купить', 'Снять', 'Посуточная аренда'])
ROOMS = Buttons(items=['Студии', '1-комнатные', '2-комнатные', '3-комнатные', '4-комнатные и более', 'Готово!'],
                order=[2, 2, 1, 1])
APARTMENT_TYPE = Buttons(items=['Новостройки', 'Вторичка', 'Все'], order=[2, 1])
PRICE = dict(rent=Buttons(items=['До 20 000 руб', 'До 30 000 руб', 'До 50 000 руб']),
             sale=Buttons(items=['До 5 000 000 руб', 'До 10 000 000 руб', 'До 15 000 000 руб']))

MAIN = Buttons(items=['Прислать квартиру', 'Уведомления', 'Настройки поиска'],
               order=[1,2])

NOTIFICATIONS = Buttons(items=[f'Ежедневно в {randint(10, 22)}ч',
                               'C 10ч до 22ч каждый час',
                               'Ежедневно в 12ч, 16ч и 20ч',
                               'тест: прямо сейчас',
                               'Отключить уведомления'])


def build_replykeyboard(buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if isinstance(buttons, Buttons):
        if buttons.order and len(buttons.items) != sum(buttons.order):
            raise ValueError("The count of buttons and their count in order list isn't equal.")

        name_is_callback = True if not isinstance(buttons.items[0], (list, tuple)) else False
        accumulated = 0
        order = buttons.order if buttons.order else [1 for _ in range(len(buttons.items))]
        for n in order:
            if name_is_callback:
                reply_buttons = [buttons.items[accumulated + i] for i in range(n)]
            else:
                reply_buttons = [buttons.items[accumulated + i][0] for i in range(n)]

            markup.row(*reply_buttons)
            accumulated += n
    elif isinstance(buttons, list):
        name_is_callback = True if not isinstance(buttons[0], (list, tuple)) else False
        for button in buttons:
            if name_is_callback:
                markup.add(button)
            else:
                markup.add(button[0])
    else:
        raise TypeError('Unknown type of buttons in app.buttons.build_replykeyboard')

    return markup


    #markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    #markup.add(*iterable)
    #return markup


def build_inlinekeyboard(buttons, row_width: int = 3):
    """
    :param buttons: list or Buttons object.
        If callback is different from the button name - list of tuples: ({button name}, {button callback data}).
    :param row_width: int.
    :return: types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup(row_width=row_width)

    if isinstance(buttons, Buttons):
        if buttons.order and len(buttons.items) != sum(buttons.order):
            raise ValueError("The count of buttons and their count in order list isn't equal.")

        name_is_callback = True if not isinstance(buttons.items[0], (list, tuple)) else False
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
        name_is_callback = True if not isinstance(buttons[0], (list, tuple)) else False
        for button in buttons:
            if name_is_callback:
                markup.add(types.InlineKeyboardButton(text=button, callback_data=button))
            else:
                markup.add(types.InlineKeyboardButton(text=button[0], callback_data=button[1]))
    else:
        raise TypeError('Unknown type of buttons in app.buttons.build_inlinekeyboard')

    return markup


EMPTY_MARKUP = types.ReplyKeyboardRemove()



