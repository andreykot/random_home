import aiogram.utils.markdown as md
from aiogram import dispatcher
from aiogram import types
from aiogram.types import ParseMode

from app import markups
from app.configs import messages


async def start(message: types.Message):
    msg = messages.START_MESSAGE
    await message.reply(msg, reply_markup=markups.EMPTY_MARKUP)
