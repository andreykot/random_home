from aiogram import executor

from app import bot


def main():
    executor.start_polling(bot.dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()
