import asyncio
from random import randint
import re
import traceback

import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, Update, callback_query
from aiogram.utils.exceptions import MessageToDeleteNotFound
from sqlalchemy.orm import Session

from app import bot_init, buttons, filters
from app import db
from app.configs import messages


async def start(message: types.Message):
    if not db.models.User.is_user(telegram_id=message.from_user.id):
        print(message.from_user.first_name, message.from_user.last_name, 'connected')
        db. models.User.insert_user(telegram_id=message.from_user.id,
                                   first_name=message.from_user.first_name,
                                   last_name=message.from_user.last_name)

    await message.reply(messages.START_MESSAGE,
                        reply_markup=buttons.build_inlinekeyboard(['Задать критерии поиска']))


async def search_terms(message: types.Message):
    try:
        db.models.UserSettings.update_current_edit_msg(telegram_id=message.from_user.id,
                                                       message_id=message.message_id)
    except Exception:
        print(traceback.print_exc())
        raise NotImplementedError

    await message.reply(messages.SEARCH_TERMS,
                        reply_markup=buttons.build_inlinekeyboard(buttons.SEARCH_TERMS))


async def get_random_flat(message: types.Message):
    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == message.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]

    flat = current_query.process_query(session)
    session.close()

    if flat:
        msg = messages.RANDOM_FLAT_ANSWER.format(flat.description, flat.url)
        await bot_init.bot.send_message(text=msg, chat_id=message.from_user.id)
    else:
        await bot_init.bot.send_message(text=messages.FLAT_ERROR, chat_id=message.from_user.id)


async def help(message: types.Message):
    pass


async def get_price_from_msg(message: types.Message):
    re_parser = re.search(r"(\d+)\s*-\s*(\d+)", message.text)
    try:
        min_price = float(re_parser[1].replace(',', '.'))
        max_price = float(re_parser[2].replace(',', '.'))
    except (IndexError, ValueError):
        await message.answer(messages.GET_PRICE_FROM_MSG_ALERT)
        return

    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == message.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    current_edit_msg = user.settings.current_edit_msg
    current_query.price = [min_price, max_price]
    db.utils.safe_commit(session)

    for i in range(message.message_id, current_edit_msg, -1):
        try:
            await bot_init.bot.delete_message(chat_id=message.from_user.id, message_id=i)
        except MessageToDeleteNotFound:
            continue

    await message.answer(messages.PRICE_ANSWER.format(int(min_price), int(max_price)),
                         disable_web_page_preview=False)
    await asyncio.sleep(2)
    await bot_init.bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id+1)


async def notifications_settings(message: types.Message):
    await message.answer(text=messages.NOTIFICATIONS_MAIN,
                         reply_markup=buttons.build_inlinekeyboard(buttons.NOTIFICATIONS))


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
        db.models.UserSettings.update_current_edit_msg(telegram_id=query.from_user.id,
                                                       message_id=query.message.message_id)
    except Exception:
        print(traceback.print_exc())
        raise NotImplementedError

    await bot_init.bot.send_message(
        text=messages.SETTINGS_FROM_START,
        chat_id=query.from_user.id,
        reply_markup=buttons.build_replykeyboard(buttons.MAIN))  # TODO плохо

    await query.answer()


async def callback_notifications(query: types.CallbackQuery):
    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]

    tasks = list()
    if re.match('Ежедневно в \d+ч', query.data):
        hour = int(re.search('Ежедневно в (\d+)ч', query.data)[1])
        task = db.models.Task(user_id=user.id,
                              task_type=1,
                              execution_hour=hour,
                              query_id=current_query.id)
        tasks.append(task)
    elif query.data == 'C 10ч до 22ч каждый час':
        for hour in range(10, 23):
            task = db.models.Task(user_id=user.id,
                                  task_type=1,
                                  execution_hour=hour,
                                  query_id=current_query.id)
            tasks.append(task)
    elif query.data == 'Ежедневно в 12ч, 16ч и 20ч':
        for hour in [12, 16, 20]:
            task = db.models.Task(user_id=user.id,
                                  task_type=1,
                                  execution_hour=hour,
                                  query_id=current_query.id)
            tasks.append(task)
    elif query.data == 'тест: прямо сейчас':
        from datetime import datetime
        task = db.models.Task(user_id=user.id,
                              task_type=1,
                              execution_hour=datetime.now().hour,
                              query_id=current_query.id)
        tasks.append(task)

    elif query.data == 'Отключить уведомления':
        session.query(db.models.Task).filter(db.models.Task.user_id == user.id).delete()
        tasks = []

    else:
        raise TypeError("Invalid query for app.handlers.callback_notifications")

    if tasks:
        session.bulk_save_objects(tasks)
    db.utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(messages.NOTIFICATIONS_ANSWER)


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
        session = Session(bind=db.models.engine)
        user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
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
        session = Session(bind=db.models.engine)
        user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
        current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]

        if current_query.deal != 'flatsale':
            items = buttons.PRICE['rent']
        else:
            items = buttons.PRICE['sale']

        await bot_init.bot.send_message(
            text=messages.GET_PRICE,
            chat_id=query.from_user.id,
            reply_markup=buttons.build_inlinekeyboard(items)
        )
    else:
        raise TypeError("Invalid query for app.handlers.callback_search_terms")

    await query.answer()


async def callback_get_city(query: types.CallbackQuery):
    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    current_query.region = filters.city_filter(query.data)
    db.utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(f'Город: {query.data}')


async def callback_get_deal_type(query: types.CallbackQuery):
    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    current_query.deal = filters.deal_filter(query.data)
    db.utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(f"Тип: {query.data}")


async def callback_get_rooms(query: types.CallbackQuery):
    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]

    if query.data != 'Готово!':
        selected_rooms_type = filters.rooms_filter(query.data, mode='to_int')

        if not current_query.rooms:
            result = {*selected_rooms_type}
        else:
            result = set(current_query.rooms)
            if selected_rooms_type not in current_query.rooms:
                for room in selected_rooms_type:
                    result.add(room)
            else:
                for room in selected_rooms_type:
                    result.remove(room)
        current_query.rooms = list(result)

        db.utils.safe_commit(session)
        await query.answer("Квартиры: {}".format(filters.rooms_filter(list(result), mode='array_to_str')))

    else:
        await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        if current_query.rooms:
            await query.answer("Количество комнат установлено!")
        else:
            await query.answer("Количество комнат не установлено")


async def callback_get_apartment_type(query: types.CallbackQuery):
    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    apartment_type = filters.apartment_type_filter(query.data)
    if apartment_type:
        current_query.apartment_type = apartment_type
        db.utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer("Тип недвижимости: {}".format(query.data))


async def callback_get_price(query: types.CallbackQuery):
    session = Session(bind=db.models.engine)
    user = session.query(db.models.User).filter(db.models.User.telegram_id == query.from_user.id).one()
    current_query = [q for q in user.queries if q.id == user.settings.editing_query][0]
    price = list(filters.price_filter(query.data))
    current_query.price = price
    db.utils.safe_commit(session)

    await bot_init.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await query.answer(messages.PRICE_ANSWER.format(int(price[0]), int(price[1])))
