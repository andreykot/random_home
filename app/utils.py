import asyncio
from collections import deque
from functools import partial
import multiprocessing
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
        if (datetime.today().hour == 4 and datetime.today().minute == 0) and day != datetime.today().day:
            db.models.ProxyList.update_table()
            day = datetime.today().day
            print("proxies updated at {}".format(datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")))
        await asyncio.sleep(50)


async def execute_db_tasks(bot_loop):
    def get_flats():
        res = [task.execute_task() for task in tasks]
        print('get_flats', res)
        return res

    while True:
        session = Session(bind=db.models.engine)
        condition = (db.models.Task.execution_hour == datetime.now().hour) and \
                    (db.models.Task.day_of_last_execution != datetime.now().day)
        tasks = session.query(db.models.Task).filter(condition).all()

        if tasks:
            #workers = len(tasks) if len(tasks) <= 10 else 10
            with ThreadPoolExecutor(max_workers=1) as pool:
                flats = await bot_loop.run_in_executor(executor=pool, func=get_flats)
                for flat, task in zip(flats, tasks):
                    print(flat, task)
                    task.day_of_last_execution = datetime.now().day
                    await bot_init.bot.send_message(text=messages.RANDOM_FLAT_ANSWER.format(flat.title, flat.link),
                                                    chat_id=task.user.telegram_id)
                    await asyncio.sleep(.05)

            db.utils.safe_commit(session)
        await asyncio.sleep(10)



