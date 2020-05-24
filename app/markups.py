from aiogram import types


def build_replykeyboard(iterable):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(*iterable)
    return markup


def build_inlinekeyboard(iterable, buttons_in_line: int = 1, row_width: int = 3):
    """
    :param iterable: list.
        If callback is different from the button name - list of tuples: ({button name}, {button callback data}).
    :param buttons_in_line: int.
        Count of buttons per line.
    :param row_width: int.
    :return: types.InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    name_is_callback = True if not isinstance(iterable[0], (list, set)) else False
    if len(iterable) % buttons_in_line == 0:
        for buttons in zip(iterable, iterable[buttons_in_line-1:]):
            if name_is_callback:
                inline_buttons = [types.InlineKeyboardButton(text=button, callback_data=button)
                                  for button in buttons]
                markup.row(*inline_buttons)
            else:
                inline_buttons = [types.InlineKeyboardButton(text=button[0], callback_data=button[1])
                                  for button in buttons]
                markup.row(*inline_buttons)
    else:
        for button in iterable:
            if name_is_callback:
                markup.add(types.InlineKeyboardButton(text=button[0], callback_data=button[1]))
            else:
                markup.add(types.InlineKeyboardButton(text=button, callback_data=button))
    return markup


EMPTY_MARKUP = types.ReplyKeyboardRemove()
