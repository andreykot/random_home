import aiogram.utils.markdown as md
from aiogram import dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from app import buttons
from app.db import db_map, utils as db_methods
from app.configs import messages
from app.CianParser.parser import get_flats_by_query, CianFlat


db_engine = db_methods.get_engine()


async def start(message: types.Message):
    if not db_map.User.is_user(engine=db_engine, telegram_id=message.from_user.id):
        db_map.User.add_user(engine=db_engine,
                             telegram_id=message.from_user.id)

    await message.reply(messages.START_MESSAGE,
                        reply_markup=buttons.build_inlinekeyboard(['Задать критерии поиска']))


async def search_terms(message: types.Message):
    await message.reply(messages.SEARCH_TERMS,
                        reply_markup=buttons.build_inlinekeyboard(buttons.SEARCH_TERMS_BUTTONS))


async def get_city(message: types.Message):
    await message.reply(messages.GET_CITY,
                        reply_markup=buttons.build_inlinekeyboard(buttons.CITY_BUTTONS))


async def get_deal_type(message: types.Message):
    await message.reply(messages.GET_DEAL_TYPE,
                        reply_markup=buttons.build_inlinekeyboard(buttons.DEAL_TYPE_BUTTONS))


async def get_rooms(message: types.Message):
    await message.reply(messages.GET_ROOMS,
                        reply_markup=buttons.build_inlinekeyboard(buttons.ROOMS_BUTTONS))


async def get_apartment_type(message: types.Message):
    await message.reply(messages.GET_APARTMENT_TYPE,
                        reply_markup=buttons.build_inlinekeyboard(buttons.APARTMENT_TYPE_BUTTONS))


async def get_price(message: types.Message):
    if True:  # TODO запрос в бд, чтобы узнать, покупка или аренда у пользователя.
        items = buttons.PRICE_BUTTONS['rent']
    else:
        items = buttons.PRICE_BUTTONS['sale']

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
