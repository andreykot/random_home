from app import handlers


def set_routes(dp):
    register = dp.register_message_handler

    register(handlers.start, commands=['start', 'about'])
