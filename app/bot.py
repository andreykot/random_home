from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.configs.bot import API_TOKEN
from app import routes


bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
#messengers = {}

routes.set_routes(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
