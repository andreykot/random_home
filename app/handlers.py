import aiogram.utils.markdown as md
from aiogram import dispatcher
from aiogram import types
from aiogram.types import ParseMode

from app import markups
from app.db import db_map, methods as db_methods
from app.configs import messages
from app.CianParser.parser import get_flats_by_query, CianFlat


async def start(message: types.Message):
    if not db_map.User.is_user(engine=db_methods.get_engine(), telegram_id=message.from_user.id):
        db_map.User.add_user(engine=db_methods.get_engine(),
                             telegram_id=message.from_user.id)

    msg = messages.START_MESSAGE
    await message.reply(msg, reply_markup=markups.EMPTY_MARKUP)


async def __test_flats_searching(message: types.Message):
    flats = get_flats_by_query()
    msg = 'Найденные квартиры:\n'
    for flat in flats:
        msg += "{}:\n{}\n\n".format(flat.title, flat.link)

    await message.reply(msg, reply_markup=markups.EMPTY_MARKUP)
