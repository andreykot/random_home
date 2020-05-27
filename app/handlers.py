import re
import traceback

import aiogram.utils.markdown as md
from aiogram import dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from sqlalchemy.orm import Session

from app import bot_init, buttons, filters
from app.db import db_map, utils
from app.configs import messages
from app.CianParser.parser import get_flats_by_query, CianFlat





async def start(message: types.Message):
    if not db_map.User.is_user(telegram_id=message.from_user.id):
        print('ok')
        db_map.User.insert_user(telegram_id=message.from_user.id)

    await message.reply(messages.START_MESSAGE,
                        reply_markup=buttons.build_inlinekeyboard(['Задать критерии поиска']))


async def search_terms(message: types.Message):
    await message.reply(messages.SEARCH_TERMS,
                        reply_markup=buttons.build_inlinekeyboard(buttons.SEARCH_TERMS))


async def get_city(message: types.Message):
    await message.reply(messages.GET_CITY,
                        reply_markup=buttons.build_inlinekeyboard(buttons.CITY))


async def get_deal_type(message: types.Message):
    await message.reply(messages.GET_DEAL_TYPE,
                        reply_markup=buttons.build_inlinekeyboard(buttons.DEAL_TYPE))


async def get_rooms(message: types.Message):
    await message.reply(messages.GET_ROOMS,
                        reply_markup=buttons.build_inlinekeyboard(buttons.ROOMS))


async def get_apartment_type(message: types.Message):
    await message.reply(messages.GET_APARTMENT_TYPE,
                        reply_markup=buttons.build_inlinekeyboard(buttons.APARTMENT_TYPE))


async def get_price(message: types.Message):
    if True:  # TODO запрос в бд, чтобы узнать, покупка или аренда у пользователя.
        items = buttons.PRICE['rent']
    else:
        items = buttons.PRICE['sale']

    await message.reply(messages.GET_PRICE,
                        reply_markup=buttons.build_inlinekeyboard(items))


async def get_random_flat(message: types.Message):
    pass


async def help(message: types.Message):
    pass


async def __test_flats_searching(message: types.Message):
    flats = get_flats_by_query()
    msg = 'Найденные квартиры:\n'
    for flat in flats:
        msg += "{}:\n{}\n\n".format(flat.title, flat.link)

    await message.reply(msg, reply_markup=buttons.EMPTY_MARKUP)


# Callback handlers

async def callback_search_terms_main(query: types.CallbackQuery):
    if query.data == 'Задать критерии поиска':
        await bot_init.bot.edit_message_text(
            text=messages.SEARCH_TERMS,
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            reply_markup=buttons.build_inlinekeyboard(buttons.SEARCH_TERMS)
        )

    try:
        db_map.UserSettings.update_current_edit_msg(telegram_id=query.from_user.id,
                                                    message_id=query.message.message_id)
    except Exception:
        print(traceback.print_exc())
        raise NotImplementedError

    await query.answer()


async def callback_search_terms(query: types.CallbackQuery):
    if query.data == 'city':
        await bot_init.bot.send_message(
            text=messages.GET_CITY,
            chat_id=query.from_user.id,
            reply_markup=buttons.build_inlinekeyboard(buttons.CITY)
        )
    elif query.data == 'deal':
        await bot_init.bot.send_message(
            text=messages.GET_DEAL_TYPE,
            chat_id=query.from_user.id,
            reply_markup=buttons.build_inlinekeyboard(buttons.DEAL_TYPE)
        )
    elif query.data == 'rooms':
        await bot_init.bot.send_message(
            text=messages.GET_ROOMS,
            chat_id=query.from_user.id,
            reply_markup=buttons.build_inlinekeyboard(buttons.ROOMS)
        )
    elif query.data == 'apart_type':
        await bot_init.bot.send_message(
            text=messages.GET_APARTMENT_TYPE,
            chat_id=query.from_user.id,
            reply_markup=buttons.build_inlinekeyboard(buttons.APARTMENT_TYPE)
        )
    elif query.data == 'price':
        if True:  # TODO запрос в бд, чтобы узнать, покупка или аренда у пользователя.
            items = buttons.PRICE['rent']
        else:
            items = buttons.PRICE['sale']
        await bot_init.bot.send_message(
            text=messages.GET_PRICE,
            chat_id=query.from_user.id,
            reply_markup=buttons.build_inlinekeyboard(items)
        )

    await query.answer()


async def callback_get_city(query: types.CallbackQuery):
    answer = None
    if query.data == 'Москва':
        answer = 'Москва'
    elif query.data == 'Санкт-Петербург':
        answer = 'Санкт-Петербург'
    else:
        raise TypeError("Unsupported city.")

    if answer:
        session = Session(bind=utils.get_engine())
        user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
        current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
        current_query.region = answer
        utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(f'Город: {answer}')


async def callback_get_deal_type(query: types.CallbackQuery):
    answer = None
    if query.data == 'Купить':
        pass
    elif query.data == 'Снять на год и более':
        pass
    elif query.data == 'Снять до года':
        pass
    elif query.data == 'Посуточная аренда':
        pass
    else:
        raise TypeError("Unsupported deal type.")

    if answer:
        message_text = query.message.text
        if re.search('Тип предложения: .+;', message_text):
            message_text = re.sub(r'\nТип предложения: (.+);', r'', message_text)

        processed_answer = "\nТип предложения: {};".format(answer)

        await bot_init.bot.edit_message_text(
            text=message_text + processed_answer,
            chat_id=query.from_user.id,
            message_id=query.message.message_id - 1,
            reply_markup=buttons.build_inlinekeyboard(buttons.SEARCH_TERMS))

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer("Тип предложения установлен!")


async def callback_get_rooms(query: types.CallbackQuery):
    if query.data == 'Студии':
        pass
    elif query.data == '1-комнатные':
        pass
    elif query.data == '2-комнатные':
        pass
    elif query.data == '3-комнатные':
        pass
    elif query.data == '4-комнатные и более':
        pass
    else:
        raise ValueError("Invalid rooms value.")

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer("Количество комнат установлено!")


async def callback_get_apartment_type(query: types.CallbackQuery):
    if query.data == 'Новостройки':
        pass
    elif query.data == 'Вторичка':
        pass
    elif query.data == 'Все':
        pass
    else:
        raise TypeError("Unsupported apartment type.")

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer("Тип недвижимости установлен!")


async def callback_get_price(query: types.CallbackQuery):
    if query.data == 'До 20 000 руб':
        pass
    elif query.data == 'До 30 000 руб':
        pass
    elif query.data == 'До 50 000 руб':
        pass
    else:
        raise ValueError("Invalid price value.")

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer("Ценовой диапазон установлен!")
