from app import handlers


def set_routes(dp):
    register = dp.register_message_handler

    register(handlers.start, commands=['start'])
    register(handlers.__test_flats_searching, commands=['test'])
