from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.configs.bot import API_TOKEN
from app import routes


bot_instance = Bot(token=API_TOKEN)

storage = MemoryStorage()
dispatcher = Dispatcher(bot_instance, storage=storage)

routes.set_routes(dispatcher)
