import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from app import db, bot
from app.configs import messages
from app.tools.ProxyPool.main import ProxyPool


async def update_proxies(bot_loop):
    day = 0
    while True:
        if (datetime.today().hour == 4 and datetime.today().minute == 0) and (day != datetime.today().day):
            proxy_pool = ProxyPool(loop=bot_loop)
            await proxy_pool.upload_proxies()
            #print("proxies updated at {}".format(datetime.now().strftime("%d-%b-%Y (%H:%M:%S)")))
        await asyncio.sleep(50)


async def execute_db_tasks(bot_loop):
    async def get_flats(session):
        flats = [await task.execute_task() for task in tasks]
        for flat, task in zip(flats, tasks):
            task.day_of_last_execution = datetime.now().day
            msg = messages.RANDOM_FLAT_ANSWER.format(
                price=flat.price,
                metro=flat.underground_txt,
                street=flat.address['street'],
                house=flat.address['house'],
                object_type=flat.info['object_type'],
                area=flat.info['area'],
                floor=flat.info['floor'],
                url=flat.url
            )
            await bot.bot_instance.send_message(text=msg,
                                                chat_id=task.user.telegram_id,
                                                parse_mode='Markdown')
            await bot.bot_instance.send_location(chat_id=task.user.telegram_id,
                                                 latitude=flat.coordinates['lat'],
                                                 longitude=flat.coordinates['lng'],
                                                 disable_notification=True)

            await asyncio.sleep(.05)
        db.utils.safe_commit(session)

    while True:
        session = Session(bind=db.models.engine)
        tasks = session.query(db.models.Task).\
            filter(db.models.Task.execution_hour == datetime.now().hour).\
            filter(db.models.Task.day_of_last_execution != datetime.now().day).\
            all()

        if tasks:
            bot_loop.create_task(get_flats(session))
        else:
            session.close()

        await asyncio.sleep(50)



