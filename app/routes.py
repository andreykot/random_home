from app import handlers, states


def set_routes(dp):
    register = dp.register_message_handler

    register(handlers.start, commands=['start'])
    register(handlers.__test_flats_searching, commands=['test'])

    register(handlers.search_terms, commands=['search_terms'])
    register(handlers.get_city, commands=['city'])
    register(handlers.get_deal_type, commands=['deal'])
    register(handlers.get_rooms, commands=['rooms'])
    register(handlers.get_apartment_type, commands=['type'])
    register(handlers.get_price, commands=['price'])

