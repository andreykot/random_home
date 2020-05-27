from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.configs.bot import API_TOKEN, PROXY_AUTH, PROXY_URL
from app import routes


bot = Bot(token=API_TOKEN, proxy_auth=PROXY_AUTH, proxy=PROXY_URL)

storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)

routes.set_routes(dispatcher)
