import asyncio
import re
import traceback

import aiogram.utils.markdown as md
from aiogram import dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Update, callback_query
from aiogram.utils.exceptions import MessageToDeleteNotFound
from sqlalchemy.orm import Session

from app import bot_init, buttons, filters
from app.db import db_map, utils
from app.configs import messages
from app.CianParser.parser import get_flats_by_query, CianFlat





async def start(message: types.Message):
    if not db_map.User.is_user(telegram_id=message.from_user.id):
        print(message.from_user.first_name, message.from_user.last_name, 'connected')
        db_map.User.insert_user(telegram_id=message.from_user.id,
                                first_name=message.from_user.first_name,
                                last_name=message.from_user.last_name)

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


async def get_price_from_msg(message: types.Message):
    re_parser = re.search(r"(\d+)\s*-\s*(\d+)", message.text)
    try:
        min_price = float(re_parser[1].replace(',', '.'))
        max_price = float(re_parser[2].replace(',', '.'))
    except (IndexError, ValueError):
        await message.answer(messages.GET_PRICE_FROM_MSG_ALERT)
        return

    session = Session(bind=utils.get_engine())
    user = session.query(db_map.User).filter(db_map.User.telegram_id == message.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    current_edit_msg = user.settings.current_edit_msg
    current_query.price = [min_price, max_price]
    utils.safe_commit(session)

    for i in range(message.message_id, current_edit_msg, -1):
        try:
            await bot_init.bot.delete_message(chat_id=message.from_user.id, message_id=i)
        except MessageToDeleteNotFound:
            continue

    await message.answer(messages.PRICE_ANSWER.format(int(min_price), int(max_price)))
    await asyncio.sleep(2)
    await bot_init.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id+1)


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
        session = Session(bind=utils.get_engine())
        user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
        current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]

        if current_query.deal == 1:
            await bot_init.bot.send_message(
                text=messages.GET_APARTMENT_TYPE,
                chat_id=query.from_user.id,
                reply_markup=buttons.build_inlinekeyboard(buttons.APARTMENT_TYPE)
            )
        else:
            await query.answer(messages.APART_TYPE_ALERT, show_alert=True)

    elif query.data == 'price':
        session = Session(bind=utils.get_engine())
        user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
        current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]

        if current_query.deal != 1:
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
    session = Session(bind=utils.get_engine())
    user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    current_query.region = query.data
    utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(f'Город: {query.data}')


async def callback_get_deal_type(query: types.CallbackQuery):
    session = Session(bind=utils.get_engine())
    user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    current_query.deal = filters.deal_filter(query.data)
    utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(f"Тип: {query.data}")


async def callback_get_rooms(query: types.CallbackQuery):
    session = Session(bind=utils.get_engine())
    user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]

    if query.data != 'Готово!':
        selected_rooms_type = filters.rooms_filter(query.data, mode='to_int')

        if not current_query.rooms:
            result = {selected_rooms_type}
        else:
            result = set(current_query.rooms)
            if selected_rooms_type not in current_query.rooms:
                result.add(selected_rooms_type)
            else:
                result.remove(selected_rooms_type)
        current_query.rooms = list(result)

        utils.safe_commit(session)
        await query.answer("Квартиры: {}".format(filters.rooms_filter(list(result), mode='array_to_str')))

    else:
        await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        if current_query.rooms:
            await query.answer("Количество комнат установлено!")
        else:
            await query.answer("Количество комнат не установлено")


async def callback_get_apartment_type(query: types.CallbackQuery):
    session = Session(bind=utils.get_engine())
    user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    current_query.apartment_type = filters.apartment_type_filter(query.data)
    utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer("Тип недвижимости: {}".format(query.data))


async def callback_get_price(query: types.CallbackQuery):
    session = Session(bind=utils.get_engine())
    user = session.query(db_map.User).filter(db_map.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    price = list(filters.price_filter(query.data))
    current_query.price = price

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(messages.PRICE_ANSWER.format(int(price[0]), int(price[1])))
