from aiogram import executor
import logging

from app import bot_init
from app.db.utils import init_db


def main():
    #logging.basicConfig(level=logging.DEBUG)
    executor.start_polling(bot_init.dispatcher, skip_updates=True)


if __name__ == '__main__':
    #init_db()
    main()
