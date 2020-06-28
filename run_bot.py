from aiogram import executor
import logging

from app import bot, utils
from app.db.utils import init_db


def main():
    logging.basicConfig(level=logging.DEBUG)

    loop = bot.dispatcher.loop
    loop.create_task(utils.update_proxies(loop))
    loop.create_task(utils.execute_db_tasks(loop))

    executor.start_polling(bot.dispatcher,
                           skip_updates=True,
                           #on_startup=utils.update_proxies_on_startup
                           )


if __name__ == '__main__':
    init_db()
    main()
