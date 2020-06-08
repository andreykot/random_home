import asyncio
from collections import deque
from functools import partial
import multiprocessing
from queue import Queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import Session

from app import db, bot_init
from app.configs import messages


async def update_proxies_on_startup(_):
    db.models.ProxyList.update_table()


async def update_proxies():
    day = 0
    while True:
        if (datetime.today().hour == 4 and datetime.today().minute == 0) and (day != datetime.today().day):
            db.models.ProxyList.update_table()
            day = datetime.today().day
            print("proxies updated at {}".format(datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")))
        await asyncio.sleep(50)


async def execute_db_tasks(bot_loop):
    def get_flats():
        res = [task.execute_task() for task in tasks]
        return res

    while True:
        session = Session(bind=db.models.engine)
        tasks = session.query(db.models.Task).\
            filter(db.models.Task.execution_hour == datetime.now().hour).\
            filter(db.models.Task.day_of_last_execution != datetime.now().day).\
            all()

        if tasks:
            flats = await bot_loop.run_in_executor(executor=None, func=get_flats)
            for flat, task in zip(flats, tasks):
                task.day_of_last_execution = datetime.now().day
                msg = messages.RANDOM_FLAT_ANSWER.format(
                    price=flat.price,
                    metro=flat.underground_txt,
                    object_type=flat.info['object_type'],
                    area=flat.info['area'],
                    floor=flat.info['floor'],
                    url=flat.url
                )
                await bot_init.bot.send_message(text=msg,
                                                chat_id=task.user.telegram_id,
                                                parse_mode='Markdown')
                await asyncio.sleep(.05)

            db.utils.safe_commit(session)
        else:
            session.close()

        await asyncio.sleep(10)



